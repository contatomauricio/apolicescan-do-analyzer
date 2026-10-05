"""Aba de Upload e Processamento."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from app.agents.orchestrator import ingerir_e_estruturar
from app.ingest.reception import ArquivoInvalidoError


def render(session: Session) -> None:
    st.header("Upload e processamento de apólices D&O")
    st.caption("Envie arquivos PDF ou imagem (PNG/JPG). O processamento roda automaticamente: texto → extração (IA) → gravação.")

    arquivos = st.file_uploader(
        "Arraste os arquivos aqui",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if arquivos and st.button("Processar arquivos", type="primary"):
        barra = st.progress(0.0, text="Iniciando...")
        total = len(arquivos)
        for indice, arquivo in enumerate(arquivos, start=1):
            barra.progress((indice - 1) / total, text=f"Processando {arquivo.name}...")
            try:
                apolice = ingerir_e_estruturar(session, arquivo.name, arquivo.read())
                st.success(f"'{arquivo.name}' processado com sucesso. Apólice id={apolice.id}, seguradora={apolice.seguradora or 'não localizado'}.")
            except ArquivoInvalidoError as erro:
                st.error(f"'{arquivo.name}': {erro}")
            except Exception as erro:  # erro de API/LLM ou validação de esquema
                st.error(f"'{arquivo.name}': falha ao processar o documento. Detalhe: {erro}")
            barra.progress(indice / total, text=f"Concluído {arquivo.name}")

    st.divider()
    st.subheader("Apólices já processadas")
    from app.db import repository

    apolices = repository.listar_apolices(session)
    if not apolices:
        st.info("Nenhuma apólice processada ainda.")
        return

    st.dataframe(
        [
            {
                "ID": a.id,
                "Seguradora": a.seguradora or "não localizado",
                "Número": a.numero or "não localizado",
                "Segurado": a.segurado or "não localizado",
                "Status": a.documento.status if a.documento else "-",
            }
            for a in apolices
        ],
        use_container_width=True,
    )
