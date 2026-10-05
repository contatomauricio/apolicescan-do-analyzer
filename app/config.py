"""Configuração central da aplicação, carregada a partir de variáveis de ambiente (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    model_extraction: str = os.getenv("GROQ_MODEL_EXTRACTION", "openai/gpt-oss-120b")
    model_qa: str = os.getenv("GROQ_MODEL_QA", "openai/gpt-oss-120b")
    model_comparison: str = os.getenv("GROQ_MODEL_COMPARISON", "openai/gpt-oss-120b")
    model_report: str = os.getenv("GROQ_MODEL_REPORT", "openai/gpt-oss-120b")

    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'insurminds.db'}")
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "data" / "uploads")))

    # Temperatura baixa para reduzir alucinação (RNF-05)
    llm_temperature: float = 0.1
    max_validation_retries: int = 2


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
