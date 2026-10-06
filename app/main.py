"""Entrypoint Streamlit: ApoliceScan — Plataforma de Análise e Comparação de Apólices D&O."""
from __future__ import annotations

import sys
from pathlib import Path

# Streamlit só adiciona ao sys.path a pasta do script (app/), não a raiz do projeto.
# Isso garante que os imports absolutos "app.xxx" funcionem ao rodar `streamlit run app/main.py`.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from app.config import settings
from app.db.database import get_session, init_db
from app.ui import compare, query, upload

st.set_page_config(page_title="ApoliceScan — Apólices D&O", layout="wide")


def main() -> None:
    init_db()

    st.title("ApoliceScan — Análise e Comparação de Apólices D&O")

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
