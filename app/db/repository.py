"""Repositório: operações de leitura e escrita no banco de dados."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Apolice, Cobertura, Comparacao, Documento, Exclusao, Franquia, Pagina
from app.schemas.apolice import ApoliceDO


def criar_documento(session: Session, nome_arquivo: str, caminho: str, tipo: str) -> Documento:
    documento = Documento(nome_arquivo=nome_arquivo, caminho=caminho, tipo=tipo, status="recebido")
    session.add(documento)
    session.flush()
    return documento


def salvar_paginas(session: Session, documento_id: int, paginas: list[tuple[int, str, bool]]) -> None:
    for numero, texto, usou_ocr in paginas:
        session.add(Pagina(documento_id=documento_id, numero=numero, texto=texto, usou_ocr=usou_ocr))
    documento = session.get(Documento, documento_id)
    if documento is not None:
        documento.paginas = len(paginas)
        documento.status = "texto_extraido"


def salvar_apolice(session: Session, documento_id: int, dados: ApoliceDO) -> Apolice:
    apolice = Apolice(
        documento_id=documento_id,
        seguradora=dados.seguradora.valor,
        numero=dados.numero_apolice.valor,
        segurado=dados.segurado.valor,
        vigencia_ini=dados.vigencia_inicio.valor,
        vigencia_fim=dados.vigencia_fim.valor,
        lmg=dados.lmg_apolice.valor,
        premio=dados.premio_total.valor,
        moeda=dados.moeda.valor,
        retroatividade=dados.retroatividade.valor,
        prazo_complementar=dados.prazo_complementar_notificacao.valor,
        base_cobertura=dados.base_cobertura.valor,
        jurisdicao=dados.jurisdicao.valor,
        json_completo=dados.model_dump(mode="json"),
    )
    session.add(apolice)
    session.flush()

    for cob in dados.coberturas:
        session.add(
            Cobertura(
                apolice_id=apolice.id,
                nome=cob.nome,
                descricao=cob.descricao,
                sublimite=cob.sublimite,
                pagina=cob.pagina,
                trecho=cob.trecho,
                confianca=cob.confianca,
            )
        )
    for fr in dados.franquias:
        session.add(
            Franquia(
                apolice_id=apolice.id,
                tipo=fr.tipo,
                valor=fr.valor,
                descricao=fr.descricao,
                pagina=fr.pagina,
                trecho=fr.trecho,
            )
        )
    for exc in dados.exclusoes:
        session.add(
            Exclusao(
                apolice_id=apolice.id,
                titulo=exc.titulo,
                descricao=exc.descricao,
                pagina=exc.pagina,
                trecho=exc.trecho,
            )
        )

    documento = session.get(Documento, documento_id)
    if documento is not None:
        documento.status = "concluido"

    return apolice


def listar_apolices(session: Session) -> list[Apolice]:
    return list(session.scalars(select(Apolice)).all())


def obter_apolice(session: Session, apolice_id: int) -> Apolice | None:
    return session.get(Apolice, apolice_id)


def obter_paginas(session: Session, documento_id: int) -> list[Pagina]:
    return list(
        session.scalars(
            select(Pagina).where(Pagina.documento_id == documento_id).order_by(Pagina.numero)
        ).all()
    )


def obter_trecho(session: Session, documento_id: int, pagina: int) -> str | None:
    registro = session.scalar(
        select(Pagina).where(Pagina.documento_id == documento_id, Pagina.numero == pagina)
    )
    return registro.texto if registro else None


def salvar_comparacao(
    session: Session, apolice_a: int, apolice_b: int, resultado_json: dict, relatorio_texto: str
) -> Comparacao:
    comparacao = Comparacao(
        apolice_a=apolice_a,
        apolice_b=apolice_b,
        resultado_json=resultado_json,
        relatorio_texto=relatorio_texto,
    )
    session.add(comparacao)
    session.flush()
    return comparacao
