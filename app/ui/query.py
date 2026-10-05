"""Aba de Consulta em linguagem natural (Q&A com citação de página)."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from app.agents.qa_agent import perguntar
from app.db import repository


def render(session: Session) -> None:
    st.header("Consulta em linguagem natural")

    apolices = repository.listar_apolices(session)
    if not apolices:
        st.info("Processe ao menos uma apólice na aba de Upload antes de consultar.")
        return

    opcoes = {f"#{a.id} — {a.seguradora or 'sem seguradora'} ({a.numero or 's/n'})": a.id for a in apolices}
    rotulo = st.selectbox("Apólice de referência", list(opcoes.keys()))
    pergunta = st.text_input(
        "Pergunta",
        placeholder="Ex.: Qual é o limite máximo de garantia? Há cobertura para custos de defesa?",
    )

    if st.button("Perguntar", type="primary") and pergunta:
        apolice_id = opcoes[rotulo]
        with st.spinner("Consultando..."):
            try:
                resposta = perguntar(session, f"[Apólice id={apolice_id}] {pergunta}")
                st.markdown(resposta)
            except Exception as erro:
                st.error(f"Não foi possível obter a resposta agora. Detalhe: {erro}")
