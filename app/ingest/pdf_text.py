"""Extração de texto nativo de PDFs por página, com fallback para OCR quando necessário."""
from __future__ import annotations

import fitz  # PyMuPDF

from app.ingest.ocr import extrair_texto_ocr_de_imagem_pdf

LIMIAR_CARACTERES_PAGINA = 30  # abaixo disso, considera-se que a página precisa de OCR


def extrair_texto_por_pagina(caminho_pdf: str) -> list[tuple[int, str, bool]]:
    """Retorna lista de (numero_pagina, texto, usou_ocr) para um PDF."""
    resultado: list[tuple[int, str, bool]] = []
    with fitz.open(caminho_pdf) as documento:
        for indice, pagina in enumerate(documento, start=1):
            texto = pagina.get_text().strip()
            usou_ocr = False
            if len(texto) < LIMIAR_CARACTERES_PAGINA:
                texto_ocr = extrair_texto_ocr_de_imagem_pdf(pagina)
                if texto_ocr.strip():
                    texto = texto_ocr.strip()
                    usou_ocr = True
            resultado.append((indice, texto, usou_ocr))
    return resultado
