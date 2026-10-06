"""Agente de Extração e Estruturação: lê o texto das páginas e devolve `ApoliceDO` validada."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior

from app.config import settings
from app.schemas.apolice import ApoliceDO

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "extraction.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

# Contas gratuitas da Groq têm um limite baixo de tokens por minuto (TPM, ~8000 no tier
# "on_demand"). Usamos a contagem de caracteres como aproximação do número de tokens e
# mantemos os blocos pequenos o bastante para caber com folga nesse teto, mesmo somando o
# overhead fixo do prompt de sistema e do schema estruturado (seção 5.2).
MAX_CARACTERES_POR_BLOCO = 9000
_STATUS_RATE_LIMIT = {413, 429}
_TENTATIVAS_RATE_LIMIT = 3
_ESPERA_RATE_LIMIT_SEGUNDOS = 65  # a janela de TPM da Groq reseta a cada 60s
# O modelo nem sempre estrutura a saída corretamente de primeira para um schema tão grande;
# uma nova tentativa com a mesma entrada frequentemente é suficiente (não é um erro determinístico).
_TENTATIVAS_VALIDACAO = 3

_agent = Agent(
    f"groq:{settings.model_extraction}",
    output_type=ApoliceDO,
    system_prompt=_SYSTEM_PROMPT,
    model_settings={"temperature": settings.llm_temperature},
    retries=settings.max_validation_retries,
)


def _formatar_bloco(paginas: list[tuple[int, str]]) -> str:
    partes = [f"--- Página {numero} ---\n{texto}" for numero, texto in paginas]
    return "\n\n".join(partes)


def _dividir_em_blocos(
    paginas: list[tuple[int, str]], max_caracteres: int = MAX_CARACTERES_POR_BLOCO
) -> list[list[tuple[int, str]]]:
    """Agrupa páginas consecutivas em blocos que não excedam `max_caracteres`.

    Garante ao menos uma página por bloco, mesmo que uma única página sozinha já
    ultrapasse o limite (nesse caso ela é enviada isolada, o que ainda pode estourar o
    rate limit, mas é tratado com retry em `_executar_bloco_com_retry`).
    """
    blocos: list[list[tuple[int, str]]] = []
    bloco_atual: list[tuple[int, str]] = []
    tamanho_atual = 0

    for pagina in paginas:
        tamanho_pagina = len(pagina[1])
        if bloco_atual and tamanho_atual + tamanho_pagina > max_caracteres:
            blocos.append(bloco_atual)
            bloco_atual = []
            tamanho_atual = 0
        bloco_atual.append(pagina)
        tamanho_atual += tamanho_pagina

    if bloco_atual:
        blocos.append(bloco_atual)

    return blocos


def _mesclar(base: ApoliceDO | None, novo: ApoliceDO) -> ApoliceDO:
    """Consolida blocos: mantém o primeiro valor com confiança maior que zero para cada campo escalar."""
    if base is None:
        return novo

    mesclado = base.model_copy(deep=True)
    for nome_campo in ApoliceDO.model_fields:
        valor_atual = getattr(mesclado, nome_campo)
        valor_novo = getattr(novo, nome_campo)
        if hasattr(valor_atual, "confianca"):
            if (valor_atual.valor is None or valor_atual.confianca == 0) and valor_novo.valor is not None:
                setattr(mesclado, nome_campo, valor_novo)

    mesclado.coberturas = base.coberturas + [c for c in novo.coberturas if c not in base.coberturas]
    mesclado.franquias = base.franquias + [f for f in novo.franquias if f not in base.franquias]
    mesclado.exclusoes = base.exclusoes + [e for e in novo.exclusoes if e not in base.exclusoes]
    return mesclado


def _executar_bloco_com_retry(texto_bloco: str) -> ApoliceDO | None:
    """Chama o LLM para um bloco, com retry/backoff para erros de rate limit da Groq e
    novas tentativas para falhas de validação do schema (o modelo nem sempre estrutura a
    saída corretamente de primeira, mas uma nova chamada frequentemente é suficiente).

    Retorna `None` (em vez de levantar) quando o bloco falha de forma não recuperável, para
    não perder o restante do documento por causa de um único bloco problemático.
    """
    tentativas_rate_limit = 0
    tentativas_validacao = 0

    while True:
        try:
            execucao = _agent.run_sync(texto_bloco)
            return execucao.output
        except ModelHTTPError as erro:
            tentativas_rate_limit += 1
            if erro.status_code not in _STATUS_RATE_LIMIT or tentativas_rate_limit >= _TENTATIVAS_RATE_LIMIT:
                raise RuntimeError(f"Erro ao chamar o modelo de extração: {erro}") from erro
            print(
                f"[extração] rate limit da Groq (tentativa {tentativas_rate_limit}/{_TENTATIVAS_RATE_LIMIT}), "
                f"aguardando {_ESPERA_RATE_LIMIT_SEGUNDOS}s antes de tentar novamente: {erro}",
                file=sys.stderr,
            )
            time.sleep(_ESPERA_RATE_LIMIT_SEGUNDOS)
        except UnexpectedModelBehavior as erro:
            tentativas_validacao += 1
            if tentativas_validacao >= _TENTATIVAS_VALIDACAO:
                print(f"[extração] bloco ignorado após falha de validação do schema: {erro}", file=sys.stderr)
                return None
            print(
                f"[extração] falha de validação do schema (tentativa {tentativas_validacao}/{_TENTATIVAS_VALIDACAO}), "
                f"tentando novamente: {erro}",
                file=sys.stderr,
            )


def extrair_apolice(paginas: list[tuple[int, str]]) -> ApoliceDO:
    """Extrai os dados estruturados de uma apólice a partir do texto por página.

    Divide o documento em blocos que caibam no limite de tokens por minuto da Groq e
    consolida o resultado. Erros de rate limit (413/429) são reenviados após uma pequena
    espera; blocos que falham na validação do schema são ignorados para não interromper
    o processamento do restante do documento (RNF-02 / seção 5.2).
    """
    resultado: ApoliceDO | None = None
    for bloco in _dividir_em_blocos(paginas):
        texto_bloco = _formatar_bloco(bloco)
        saida = _executar_bloco_com_retry(texto_bloco)
        if saida is not None:
            resultado = _mesclar(resultado, saida)

    if resultado is None:
        resultado = ApoliceDO()
    return resultado
