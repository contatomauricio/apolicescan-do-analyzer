"""Agente de recepção: valida o upload, salva o arquivo e registra o documento no banco."""
from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.db import repository
from app.db.models import Documento
from app.ingest.ocr import extrair_texto_ocr_de_arquivo_imagem
from app.ingest.pdf_text import extrair_texto_por_pagina

EXTENSOES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg"}
TAMANHO_MAXIMO_BYTES = 25 * 1024 * 1024  # 25 MB


class ArquivoInvalidoError(Exception):
    pass


def validar_arquivo(nome_arquivo: str, tamanho_bytes: int) -> str:
    extensao = Path(nome_arquivo).suffix.lower()
    if extensao not in EXTENSOES_PERMITIDAS:
        raise ArquivoInvalidoError(f"Formato não suportado: {extensao}. Use PDF, PNG ou JPG.")
    if tamanho_bytes > TAMANHO_MAXIMO_BYTES:
        raise ArquivoInvalidoError("Arquivo excede o tamanho máximo permitido (25 MB).")
    return extensao


def salvar_arquivo_enviado(nome_arquivo: str, conteudo: bytes) -> Path:
    extensao = Path(nome_arquivo).suffix.lower()
    nome_unico = f"{uuid.uuid4().hex}{extensao}"
    destino = settings.upload_dir / nome_unico
    with open(destino, "wb") as arquivo:
        arquivo.write(conteudo)
    return destino


def processar_upload(session: Session, nome_arquivo: str, conteudo: bytes) -> Documento:
    """Valida, salva e extrai o texto de um arquivo recém-enviado. Não faz chamadas de LLM."""
    tamanho = len(conteudo)
    extensao = validar_arquivo(nome_arquivo, tamanho)

    destino = salvar_arquivo_enviado(nome_arquivo, conteudo)
    tipo = "pdf" if extensao == ".pdf" else "imagem"
    documento = repository.criar_documento(session, nome_arquivo, str(destino), tipo)

    try:
        if tipo == "pdf":
            paginas = extrair_texto_por_pagina(str(destino))
        else:
            texto = extrair_texto_ocr_de_arquivo_imagem(str(destino))
            paginas = [(1, texto, True)]
    except Exception as erro:
        documento.status = "erro_extracao_texto"
        raise ArquivoInvalidoError(f"Falha ao ler o documento: {erro}") from erro

    if not any(texto.strip() for _, texto, _ in paginas):
        documento.status = "erro_sem_texto"
        raise ArquivoInvalidoError("Não foi possível extrair texto do documento (PDF ilegível ou vazio).")

    repository.salvar_paginas(session, documento.id, paginas)
    return documento


def remover_arquivo(caminho: str) -> None:
    Path(caminho).unlink(missing_ok=True)
