"""Agente de Relatório: redige o resumo executivo comparativo em linguagem natural."""
from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent

from app.config import settings
from app.schemas.apolice import ResultadoComparacao

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "report.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

_agent = Agent(
    f"groq:{settings.model_report}",
    output_type=str,
    system_prompt=_SYSTEM_PROMPT,
    model_settings={"temperature": settings.llm_temperature},
)


def gerar_relatorio(resultado: ResultadoComparacao) -> str:
    linhas = [
        f"- [{d.categoria}] {d.item}: A={d.valor_a!r} B={d.valor_b!r} "
        f"status={d.status.value} impacto={d.impacto.value} — {d.explicacao}"
        for d in resultado.diferencas
    ]
    prompt = "Diferenças encontradas:\n" + "\n".join(linhas)
    execucao = _agent.run_sync(prompt)
    return execucao.output
