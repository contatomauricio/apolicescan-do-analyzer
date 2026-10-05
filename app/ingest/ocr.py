"""OCR com Tesseract, usado como fallback quando o PDF não tem texto nativo suficiente."""
from __future__ import annotations

import io

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

DPI_RENDER = 300


def extrair_texto_ocr_de_imagem_pdf(pagina: "fitz.Page") -> str:
    """Renderiza a página em alta resolução e aplica OCR."""
    pixmap = pagina.get_pixmap(dpi=DPI_RENDER)
    imagem = Image.open(io.BytesIO(pixmap.tobytes("png")))
    try:
        return pytesseract.image_to_string(imagem, lang="por")
    except pytesseract.TesseractNotFoundError:
        return ""


def extrair_texto_ocr_de_arquivo_imagem(caminho_imagem: str) -> str:
    """OCR direto para arquivos de imagem (PNG/JPG) enviados pelo usuário."""
    imagem = Image.open(caminho_imagem)
    try:
        return pytesseract.image_to_string(imagem, lang="por")
    except pytesseract.TesseractNotFoundError:
        return ""
