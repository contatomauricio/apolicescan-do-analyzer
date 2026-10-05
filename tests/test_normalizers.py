from datetime import date

from app.services.normalizers import normalizar_data, normalizar_moeda, normalizar_percentual


def test_normalizar_moeda_formato_brasileiro():
    assert normalizar_moeda("R$ 10.000.000,00") == 10_000_000.00


def test_normalizar_moeda_sem_simbolo():
    assert normalizar_moeda("1.500,50") == 1500.50


def test_normalizar_moeda_vazio_retorna_none():
    assert normalizar_moeda(None) is None
    assert normalizar_moeda("") is None


def test_normalizar_percentual():
    assert normalizar_percentual("10%") == 10.0
    assert normalizar_percentual("10,5 %") == 10.5


def test_normalizar_data_formato_numerico():
    assert normalizar_data("12/08/2026") == date(2026, 8, 12)


def test_normalizar_data_formato_extenso():
    assert normalizar_data("12 de agosto de 2026") == date(2026, 8, 12)


def test_normalizar_data_iso():
    assert normalizar_data("2026-08-12") == date(2026, 8, 12)


def test_normalizar_data_invalida_retorna_none():
    assert normalizar_data("não é uma data") is None
