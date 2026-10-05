"""Entrypoint Streamlit: InsurMinds — Plataforma de Análise e Comparação de Apólices D&O."""
from __future__ import annotations

import streamlit as st

from app.config import settings
from app.db.database import get_session, init_db
from app.ui import compare, query, upload

st.set_page_config(page_title="InsurMinds — Apólices D&O", layout="wide")


def main() -> None:
    init_db()

    st.title("InsurMinds — Análise e Comparação de Apólices D&O")

    if not settings.groq_api_key:
        st.warning(
            "GROQ_API_KEY não configurada. Defina a variável no arquivo .env para habilitar "
            "a extração, consulta e comparação (que dependem do LLM)."
        )

    aba_upload, aba_consulta, aba_comparacao = st.tabs(["Upload e processamento", "Consulta", "Comparação"])

    with get_session() as session:
        with aba_upload:
            upload.render(session)
        with aba_consulta:
            query.render(session)
        with aba_comparacao:
            compare.render(session)


if __name__ == "__main__":
    main()
