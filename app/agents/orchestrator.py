"""Orquestrador: coordena recepção, extração, persistência, comparação e relatório."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.comparison_agent import comparar_apolices
from app.agents.extraction_agent import extrair_apolice
from app.agents.report_agent import gerar_relatorio
from app.db import repository
from app.db.models import Apolice, Documento
from app.ingest.reception import processar_upload
from app.schemas.apolice import ResultadoComparacao


def ingerir_e_estruturar(session: Session, nome_arquivo: str, conteudo: bytes) -> Apolice:
    """Fluxo completo de um upload: recepção -> texto -> extração (LLM) -> persistência."""
    documento: Documento = processar_upload(session, nome_arquivo, conteudo)

    paginas = repository.obter_paginas(session, documento.id)
    texto_paginas = [(p.numero, p.texto) for p in paginas]

    documento.status = "extraindo_campos"
    dados = extrair_apolice(texto_paginas)

    apolice = repository.salvar_apolice(session, documento.id, dados)
    return apolice


def comparar_e_relatar(session: Session, apolice_id_a: int, apolice_id_b: int) -> tuple[ResultadoComparacao, str]:
    """Fluxo completo de comparação: diff híbrido -> relatório em linguagem natural -> persistência."""
    apolice_a = repository.obter_apolice(session, apolice_id_a)
    apolice_b = repository.obter_apolice(session, apolice_id_b)
    if apolice_a is None or apolice_b is None:
        raise ValueError("Uma das apólices selecionadas não foi encontrada.")

    resultado = comparar_apolices(apolice_a, apolice_b)
    relatorio = gerar_relatorio(resultado)
    resultado.resumo_executivo = relatorio

    repository.salvar_comparacao(
        session,
        apolice_a=apolice_id_a,
        apolice_b=apolice_id_b,
        resultado_json=resultado.model_dump(mode="json"),
        relatorio_texto=relatorio,
    )
    return resultado, relatorio
