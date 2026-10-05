"""Agente de Comparação: combina diff determinístico (código) com análise semântica de cláusulas (LLM)."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent

from app.config import settings
from app.db.models import Apolice
from app.schemas.apolice import Diferenca, ResultadoComparacao
from app.services.comparator import comparar_campos_deterministicos

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "comparison.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


class _ListaDiferencas(BaseModel):
    diferencas: list[Diferenca]


_agent = Agent(
    f"groq:{settings.model_comparison}",
    output_type=_ListaDiferencas,
    system_prompt=_SYSTEM_PROMPT,
    model_settings={"temperature": settings.llm_temperature},
    retries=settings.max_validation_retries,
)


def _formatar_itens_textuais(categoria: str, itens_a: list, itens_b: list, campo_nome: str, campo_desc: str) -> str:
    linhas = [f"Categoria: {categoria}"]
    linhas.append("Apólice A:")
    for item in itens_a:
        linhas.append(f"- {getattr(item, campo_nome)}: {getattr(item, campo_desc) or ''} (página {item.pagina})")
    linhas.append("Apólice B:")
    for item in itens_b:
        linhas.append(f"- {getattr(item, campo_nome)}: {getattr(item, campo_desc) or ''} (página {item.pagina})")
    return "\n".join(linhas)


def comparar_clausulas_textuais(apolice_a: Apolice, apolice_b: Apolice) -> list[Diferenca]:
    """Usa o LLM apenas para comparar texto de exclusões e coberturas (seção 5.3)."""
    prompt_exclusoes = _formatar_itens_textuais(
        "Exclusões", apolice_a.exclusoes, apolice_b.exclusoes, "titulo", "descricao"
    )
    prompt_coberturas = _formatar_itens_textuais(
        "Coberturas", apolice_a.coberturas, apolice_b.coberturas, "nome", "descricao"
    )

    diferencas: list[Diferenca] = []
    for prompt in (prompt_exclusoes, prompt_coberturas):
        execucao = _agent.run_sync(prompt)
        diferencas.extend(execucao.output.diferencas)
    return diferencas


def comparar_apolices(apolice_a: Apolice, apolice_b: Apolice) -> ResultadoComparacao:
    diferencas = comparar_campos_deterministicos(apolice_a, apolice_b)
    diferencas.extend(comparar_clausulas_textuais(apolice_a, apolice_b))
    return ResultadoComparacao(apolice_a_id=apolice_a.id, apolice_b_id=apolice_b.id, diferencas=diferencas)
