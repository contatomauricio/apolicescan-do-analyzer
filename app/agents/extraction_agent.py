"""Agente de Extração e Estruturação: lê o texto das páginas e devolve `ApoliceDO` validada."""
from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError
from pydantic_ai import Agent

from app.config import settings
from app.schemas.apolice import ApoliceDO

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "extraction.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

PAGINAS_POR_BLOCO = 12  # janela de páginas por chamada, para apólices longas (seção 5.2)

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


def extrair_apolice(paginas: list[tuple[int, str]]) -> ApoliceDO:
    """Extrai os dados estruturados de uma apólice a partir do texto por página.

    Divide o documento em blocos de páginas quando necessário e consolida o resultado.
    A validação do esquema Pydantic acontece automaticamente; `pydantic-ai` reenvia o erro
    ao modelo e tenta novamente até `max_validation_retries` vezes (RNF-02 / seção 5.2).
    """
    resultado: ApoliceDO | None = None
    for inicio in range(0, len(paginas), PAGINAS_POR_BLOCO):
        bloco = paginas[inicio : inicio + PAGINAS_POR_BLOCO]
        texto_bloco = _formatar_bloco(bloco)
        try:
            execucao = _agent.run_sync(texto_bloco)
        except ValidationError as erro:
            raise RuntimeError(f"Resposta do LLM fora do esquema após as tentativas de retry: {erro}") from erro
        resultado = _mesclar(resultado, execucao.output)

    if resultado is None:
        resultado = ApoliceDO()
    return resultado
