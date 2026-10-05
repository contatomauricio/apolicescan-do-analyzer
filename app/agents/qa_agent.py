"""Agente de Consulta (Q&A): responde perguntas em linguagem natural usando tools sobre o banco."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext
from sqlalchemy.orm import Session

from app.config import settings
from app.tools import db_tools

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "qa.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


@dataclass
class QADependencies:
    session: Session


qa_agent = Agent(
    f"groq:{settings.model_qa}",
    deps_type=QADependencies,
    system_prompt=_SYSTEM_PROMPT,
    model_settings={"temperature": settings.llm_temperature},
)


@qa_agent.tool
def listar_apolices(ctx: RunContext[QADependencies]) -> list[dict]:
    return db_tools.listar_apolices(ctx.deps.session)


@qa_agent.tool
def obter_apolice(ctx: RunContext[QADependencies], apolice_id: int) -> dict | None:
    return db_tools.obter_apolice(ctx.deps.session, apolice_id)


@qa_agent.tool
def buscar_clausula(ctx: RunContext[QADependencies], apolice_id: int, termo: str) -> list[dict]:
    return db_tools.buscar_clausula(ctx.deps.session, apolice_id, termo)


@qa_agent.tool
def comparar_apolices(ctx: RunContext[QADependencies], id_a: int, id_b: int) -> dict:
    return db_tools.comparar_apolices_resumo(ctx.deps.session, id_a, id_b)


@qa_agent.tool
def obter_trecho(ctx: RunContext[QADependencies], apolice_id: int, pagina: int) -> str | None:
    return db_tools.obter_trecho(ctx.deps.session, apolice_id, pagina)


def perguntar(session: Session, pergunta: str) -> str:
    resultado = qa_agent.run_sync(pergunta, deps=QADependencies(session=session))
    return resultado.output
