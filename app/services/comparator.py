"""Comparador determinístico: campos numéricos e datas são comparados diretamente em código.

A comparação semântica de cláusulas textuais (exclusões, coberturas) fica a cargo do
`comparison_agent`, que usa LLM apenas onde o código não pode decidir com exatidão.
"""
from __future__ import annotations

import datetime as dt

from app.db.models import Apolice
from app.schemas.apolice import Citacao, Diferenca, Impacto, StatusDiferenca


def _classificar_status(valor_a: object | None, valor_b: object | None) -> StatusDiferenca:
    if valor_a is None and valor_b is not None:
        return StatusDiferenca.SOMENTE_EM_B
    if valor_a is not None and valor_b is None:
        return StatusDiferenca.SOMENTE_EM_A
    if valor_a == valor_b:
        return StatusDiferenca.IGUAL
    return StatusDiferenca.DIFERENTE


def _diferenca_numerica(categoria: str, item: str, valor_a: float | None, valor_b: float | None, impacto: Impacto) -> Diferenca:
    status = _classificar_status(valor_a, valor_b)
    explicacao = "Valores idênticos."
    if status == StatusDiferenca.DIFERENTE and valor_a is not None and valor_b is not None:
        diferenca_absoluta = valor_b - valor_a
        diferenca_percentual = (diferenca_absoluta / valor_a * 100) if valor_a else None
        if diferenca_percentual is not None:
            explicacao = f"Diferença de {diferenca_absoluta:,.2f} ({diferenca_percentual:+.1f}%)."
        else:
            explicacao = f"Diferença de {diferenca_absoluta:,.2f}."
    elif status in (StatusDiferenca.SOMENTE_EM_A, StatusDiferenca.SOMENTE_EM_B):
        explicacao = "Campo presente em apenas uma das apólices."

    return Diferenca(
        categoria=categoria,
        item=item,
        valor_a=None if valor_a is None else str(valor_a),
        valor_b=None if valor_b is None else str(valor_b),
        status=status,
        impacto=impacto if status != StatusDiferenca.IGUAL else Impacto.BAIXO,
        explicacao=explicacao,
    )


def _diferenca_data(categoria: str, item: str, valor_a: dt.date | None, valor_b: dt.date | None, impacto: Impacto) -> Diferenca:
    status = _classificar_status(valor_a, valor_b)
    explicacao = "Datas idênticas."
    if status == StatusDiferenca.DIFERENTE and valor_a and valor_b:
        dias = (valor_b - valor_a).days
        explicacao = f"Diferença de {abs(dias)} dia(s)."
    elif status in (StatusDiferenca.SOMENTE_EM_A, StatusDiferenca.SOMENTE_EM_B):
        explicacao = "Data presente em apenas uma das apólices."

    return Diferenca(
        categoria=categoria,
        item=item,
        valor_a=valor_a.isoformat() if valor_a else None,
        valor_b=valor_b.isoformat() if valor_b else None,
        status=status,
        impacto=impacto if status != StatusDiferenca.IGUAL else Impacto.BAIXO,
        explicacao=explicacao,
    )


def comparar_campos_deterministicos(apolice_a: Apolice, apolice_b: Apolice) -> list[Diferenca]:
    """Compara limite, retenção, vigência e prêmio diretamente em código (seção 5.3)."""
    diferencas = [
        _diferenca_numerica("Valores", "Limite Máximo de Garantia (LMG)", apolice_a.lmg, apolice_b.lmg, Impacto.ALTO),
        _diferenca_numerica("Valores", "Prêmio total", apolice_a.premio, apolice_b.premio, Impacto.MEDIO),
        _diferenca_data("Condições temporais", "Início de vigência", apolice_a.vigencia_ini, apolice_b.vigencia_ini, Impacto.MEDIO),
        _diferenca_data("Condições temporais", "Fim de vigência", apolice_a.vigencia_fim, apolice_b.vigencia_fim, Impacto.MEDIO),
        _diferenca_data("Condições temporais", "Retroatividade", apolice_a.retroatividade, apolice_b.retroatividade, Impacto.ALTO),
    ]

    status_base_cobertura = _classificar_status(apolice_a.base_cobertura, apolice_b.base_cobertura)
    diferencas.append(
        Diferenca(
            categoria="Condições temporais",
            item="Base de cobertura",
            valor_a=apolice_a.base_cobertura,
            valor_b=apolice_b.base_cobertura,
            status=status_base_cobertura,
            impacto=Impacto.ALTO if status_base_cobertura == StatusDiferenca.DIFERENTE else Impacto.BAIXO,
            explicacao="Bases de cobertura distintas." if status_base_cobertura == StatusDiferenca.DIFERENTE else "Mesma base de cobertura.",
        )
    )

    status_moeda = _classificar_status(apolice_a.moeda, apolice_b.moeda)
    diferencas.append(
        Diferenca(
            categoria="Valores",
            item="Moeda",
            valor_a=apolice_a.moeda,
            valor_b=apolice_b.moeda,
            status=status_moeda,
            impacto=Impacto.MEDIO if status_moeda == StatusDiferenca.DIFERENTE else Impacto.BAIXO,
            explicacao="Moedas distintas, atenção à conversão." if status_moeda == StatusDiferenca.DIFERENTE else "Mesma moeda.",
        )
    )

    return diferencas


def citacao_de_exclusao(exclusao) -> Citacao:
    return Citacao(pagina=exclusao.pagina, trecho=exclusao.trecho)
