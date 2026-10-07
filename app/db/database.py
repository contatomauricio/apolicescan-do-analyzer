"""Engine e sessão SQLAlchemy."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.models import Base

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False, "timeout": 30})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(Engine, "connect")
def _habilitar_wal_sqlite(conexao_dbapi, _registro_conexao) -> None:
    """Ativa o modo WAL do SQLite: permite leituras concorrentes enquanto há uma escrita em
    andamento, reduzindo os erros "database is locked" quando várias conexões acessam o
    mesmo arquivo (ex.: app + scripts de diagnóstico rodando ao mesmo tempo)."""
    cursor = conexao_dbapi.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
