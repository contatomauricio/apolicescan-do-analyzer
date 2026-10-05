"""Tools expostas ao agente de consulta (Q&A), operando sobre o banco SQLite (seção 6.3)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import repository
from app.db.models import Apolice


def listar_apolices(session: Session) -> list[dict]:
    apolices = repository.listar_apolices(session)
    return [
        {"id": a.id, "seguradora": a.seguradora, "numero": a.numero, "segurado": a.segurado}
        for a in apolices
    ]


def obter_apolice(session: Session, apolice_id: int) -> dict | None:
    apolice = repository.obter_apolice(session, apolice_id)
    if apolice is None:
        return None
    return apolice.json_completo


def buscar_clausula(session: Session, apolice_id: int, termo: str) -> list[dict]:
    """Busca o termo no texto das páginas do documento e nas cláusulas (coberturas/exclusões)."""
    apolice = repository.obter_apolice(session, apolice_id)
    if apolice is None:
        return []

    termo_lower = termo.lower()
    resultados: list[dict] = []

    for pagina in repository.obter_paginas(session, apolice.documento_id):
        if termo_lower in pagina.texto.lower():
            resultados.append({"origem": "texto_pagina", "pagina": pagina.numero, "trecho": pagina.texto[:500]})

    for exclusao in apolice.exclusoes:
        alvo = f"{exclusao.titulo} {exclusao.descricao or ''}".lower()
        if termo_lower in alvo:
            resultados.append({"origem": "exclusao", "pagina": exclusao.pagina, "trecho": exclusao.descricao or exclusao.titulo})

    for cobertura in apolice.coberturas:
        alvo = f"{cobertura.nome} {cobertura.descricao or ''}".lower()
        if termo_lower in alvo:
            resultados.append({"origem": "cobertura", "pagina": cobertura.pagina, "trecho": cobertura.descricao or cobertura.nome})

    return resultados


def obter_trecho(session: Session, apolice_id: int, pagina: int) -> str | None:
    apolice = repository.obter_apolice(session, apolice_id)
    if apolice is None:
        return None
    return repository.obter_trecho(session, apolice.documento_id, pagina)


def comparar_apolices_resumo(session: Session, id_a: int, id_b: int) -> dict:
    """Resumo rápido (sem LLM) usado pelo agente de consulta para responder perguntas comparativas simples."""
    a: Apolice | None = repository.obter_apolice(session, id_a)
    b: Apolice | None = repository.obter_apolice(session, id_b)
    if a is None or b is None:
        return {"erro": "Uma das apólices não foi encontrada."}
    return {
        "apolice_a": {"id": a.id, "seguradora": a.seguradora, "lmg": a.lmg, "premio": a.premio},
        "apolice_b": {"id": b.id, "seguradora": b.seguradora, "lmg": b.lmg, "premio": b.premio},
    }
