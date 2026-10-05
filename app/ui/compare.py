"""Aba de Comparação entre duas apólices."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from app.agents.orchestrator import comparar_e_relatar
from app.db import repository

_COR_POR_STATUS = {
    "igual": "#d4edda",
    "diferente": "#fff3cd",
    "somente_em_A": "#d1ecf1",
    "somente_em_B": "#f8d7da",
}


def _destacar_status(linha: pd.Series) -> list[str]:
    cor = _COR_POR_STATUS.get(linha["status"], "")
    return [f"background-color: {cor}"] * len(linha)


def render(session: Session) -> None:
    st.header("Comparação de apólices")

    apolices = repository.listar_apolices(session)
    if len(apolices) < 2:
        st.info("É necessário ter ao menos 2 apólices processadas para comparar.")
        return

    opcoes = {f"#{a.id} — {a.seguradora or 'sem seguradora'} ({a.numero or 's/n'})": a.id for a in apolices}
    coluna_a, coluna_b = st.columns(2)
    with coluna_a:
        rotulo_a = st.selectbox("Apólice A", list(opcoes.keys()), key="apolice_a")
    with coluna_b:
        rotulo_b = st.selectbox("Apólice B", list(opcoes.keys()), index=min(1, len(opcoes) - 1), key="apolice_b")

    if st.button("Comparar", type="primary"):
        id_a, id_b = opcoes[rotulo_a], opcoes[rotulo_b]
        if id_a == id_b:
            st.warning("Selecione duas apólices diferentes.")
            return
        with st.spinner("Comparando apólices..."):
            try:
                resultado, relatorio = comparar_e_relatar(session, id_a, id_b)
            except Exception as erro:
                st.error(f"Não foi possível concluir a comparação agora. Detalhe: {erro}")
                return

        st.subheader("Resumo executivo")
        st.markdown(relatorio)

        st.subheader("Diferenças lado a lado")
        dados = [
            {
                "Categoria": d.categoria,
                "Item": d.item,
                "Apólice A": d.valor_a or "-",
                "Apólice B": d.valor_b or "-",
                "status": d.status.value,
                "Impacto": d.impacto.value,
                "Explicação": d.explicacao,
            }
            for d in resultado.diferencas
        ]
        tabela = pd.DataFrame(dados)
        st.dataframe(tabela.style.apply(_destacar_status, axis=1), use_container_width=True)

        st.download_button(
            "Exportar relatório (Markdown)",
            data=relatorio,
            file_name=f"comparacao_{id_a}_vs_{id_b}.md",
            mime="text/markdown",
        )
