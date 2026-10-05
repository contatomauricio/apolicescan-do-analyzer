"""Normalizadores de valores monetários, datas e percentuais (feitos em código, não no LLM)."""
from __future__ import annotations

import datetime as dt
import re

_MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def normalizar_moeda(texto: str | None) -> float | None:
    """Converte 'R$ 10.000.000,00' ou '10.000.000,00' em 10000000.0."""
    if not texto:
        return None
    limpo = re.sub(r"[^\d,.-]", "", texto).strip()
    if not limpo:
        return None
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def normalizar_percentual(texto: str | None) -> float | None:
    """Converte '10%' ou '10,5 %' em 10.5."""
    if not texto:
        return None
    limpo = texto.replace("%", "").strip().replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def normalizar_data(texto: str | None) -> dt.date | None:
    """Converte datas em formatos comuns pt-BR ('12/08/2026', '12 de agosto de 2026') em date."""
    if not texto:
        return None
    texto = texto.strip()

    match_numerico = re.match(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})$", texto)
    if match_numerico:
        dia, mes, ano = match_numerico.groups()
        ano_int = int(ano) if len(ano) == 4 else 2000 + int(ano)
        try:
            return dt.date(ano_int, int(mes), int(dia))
        except ValueError:
            return None

    match_extenso = re.match(r"^(\d{1,2}) de ([a-zç]+) de (\d{4})$", texto.lower())
    if match_extenso:
        dia, mes_nome, ano = match_extenso.groups()
        mes = _MESES_PT.get(mes_nome)
        if mes:
            try:
                return dt.date(int(ano), mes, int(dia))
            except ValueError:
                return None

    match_iso = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", texto)
    if match_iso:
        try:
            return dt.date(int(match_iso[1]), int(match_iso[2]), int(match_iso[3]))
        except ValueError:
            return None

    return None
