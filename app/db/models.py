"""Modelos SQLAlchemy (tabelas da seção 8.2 da spec)."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Documento(Base):
    __tablename__ = "documento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    caminho: Mapped[str] = mapped_column(String(500))
    tipo: Mapped[str] = mapped_column(String(20))
    paginas: Mapped[int] = mapped_column(Integer, default=0)
    enviado_em: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="recebido")

    paginas_texto: Mapped[list["Pagina"]] = relationship(back_populates="documento", cascade="all, delete-orphan")
    apolice: Mapped["Apolice | None"] = relationship(back_populates="documento", uselist=False, cascade="all, delete-orphan")


class Pagina(Base):
    __tablename__ = "pagina"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documento.id"))
    numero: Mapped[int] = mapped_column(Integer)
    texto: Mapped[str] = mapped_column(Text, default="")
    usou_ocr: Mapped[bool] = mapped_column(Boolean, default=False)

    documento: Mapped[Documento] = relationship(back_populates="paginas_texto")


class Apolice(Base):
    __tablename__ = "apolice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documento.id"))
    seguradora: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(100), nullable=True)
    segurado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vigencia_ini: Mapped[dt.date | None] = mapped_column(nullable=True)
    vigencia_fim: Mapped[dt.date | None] = mapped_column(nullable=True)
    lmg: Mapped[float | None] = mapped_column(Float, nullable=True)
    premio: Mapped[float | None] = mapped_column(Float, nullable=True)
    moeda: Mapped[str | None] = mapped_column(String(10), nullable=True)
    retroatividade: Mapped[dt.date | None] = mapped_column(nullable=True)
    prazo_complementar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    base_cobertura: Mapped[str | None] = mapped_column(String(100), nullable=True)
    jurisdicao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    json_completo: Mapped[dict] = mapped_column(JSON, default=dict)

    documento: Mapped[Documento] = relationship(back_populates="apolice")
    coberturas: Mapped[list["Cobertura"]] = relationship(back_populates="apolice", cascade="all, delete-orphan")
    franquias: Mapped[list["Franquia"]] = relationship(back_populates="apolice", cascade="all, delete-orphan")
    exclusoes: Mapped[list["Exclusao"]] = relationship(back_populates="apolice", cascade="all, delete-orphan")


class Cobertura(Base):
    __tablename__ = "cobertura"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apolice_id: Mapped[int] = mapped_column(ForeignKey("apolice.id"))
    nome: Mapped[str] = mapped_column(String(255))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    sublimite: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pagina: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trecho: Mapped[str | None] = mapped_column(Text, nullable=True)
    confianca: Mapped[float] = mapped_column(Float, default=0.0)

    apolice: Mapped[Apolice] = relationship(back_populates="coberturas")


class Franquia(Base):
    __tablename__ = "franquia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apolice_id: Mapped[int] = mapped_column(ForeignKey("apolice.id"))
    tipo: Mapped[str] = mapped_column(String(100))
    valor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    pagina: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trecho: Mapped[str | None] = mapped_column(Text, nullable=True)

    apolice: Mapped[Apolice] = relationship(back_populates="franquias")


class Exclusao(Base):
    __tablename__ = "exclusao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apolice_id: Mapped[int] = mapped_column(ForeignKey("apolice.id"))
    titulo: Mapped[str] = mapped_column(String(255))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    pagina: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trecho: Mapped[str | None] = mapped_column(Text, nullable=True)

    apolice: Mapped[Apolice] = relationship(back_populates="exclusoes")


class Comparacao(Base):
    __tablename__ = "comparacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apolice_a: Mapped[int] = mapped_column(ForeignKey("apolice.id"))
    apolice_b: Mapped[int] = mapped_column(ForeignKey("apolice.id"))
    criado_em: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    resultado_json: Mapped[dict] = mapped_column(JSON, default=dict)
    relatorio_texto: Mapped[str | None] = mapped_column(Text, nullable=True)
