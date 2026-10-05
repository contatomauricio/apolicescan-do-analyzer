from app.db.models import Apolice
from app.schemas.apolice import Impacto, StatusDiferenca
from app.services.comparator import comparar_campos_deterministicos


def _apolice(**kwargs) -> Apolice:
    base = {
        "id": 1,
        "documento_id": 1,
        "lmg": 10_000_000.0,
        "premio": 50_000.0,
        "moeda": "BRL",
        "base_cobertura": "claims made",
    }
    base.update(kwargs)
    return Apolice(**base)


def test_lmg_igual_classificado_como_igual():
    a = _apolice(lmg=10_000_000.0)
    b = _apolice(lmg=10_000_000.0)
    diferencas = comparar_campos_deterministicos(a, b)
    item = next(d for d in diferencas if d.item == "Limite Máximo de Garantia (LMG)")
    assert item.status == StatusDiferenca.IGUAL


def test_lmg_diferente_classificado_e_com_impacto_alto():
    a = _apolice(lmg=10_000_000.0)
    b = _apolice(lmg=5_000_000.0)
    diferencas = comparar_campos_deterministicos(a, b)
    item = next(d for d in diferencas if d.item == "Limite Máximo de Garantia (LMG)")
    assert item.status == StatusDiferenca.DIFERENTE
    assert item.impacto == Impacto.ALTO


def test_campo_somente_em_a():
    a = _apolice(premio=50_000.0)
    b = _apolice(premio=None)
    diferencas = comparar_campos_deterministicos(a, b)
    item = next(d for d in diferencas if d.item == "Prêmio total")
    assert item.status == StatusDiferenca.SOMENTE_EM_A


def test_base_cobertura_diferente():
    a = _apolice(base_cobertura="claims made")
    b = _apolice(base_cobertura="occurrence")
    diferencas = comparar_campos_deterministicos(a, b)
    item = next(d for d in diferencas if d.item == "Base de cobertura")
    assert item.status == StatusDiferenca.DIFERENTE
    assert item.impacto == Impacto.ALTO
