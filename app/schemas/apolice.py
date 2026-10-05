"""Esquemas Pydantic do domínio: campos extraídos, apólice D&O e diferenças de comparação.

Toda informação extraída por LLM é encapsulada em `Campo`, que carrega a página e o
trecho de origem, além de um nível de confiança. Campos não localizados devem ser
representados com `valor=None`, nunca inventados (RNF-06).
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Campo(BaseModel, Generic[T]):
    """Valor extraído com rastreabilidade até a fonte no documento."""

    valor: T | None = Field(default=None, description="Valor normalizado do campo, ou None se não localizado")
    pagina: int | None = Field(default=None, description="Página do documento onde o campo foi encontrado")
    trecho_origem: str | None = Field(default=None, description="Trecho literal do texto que originou o valor")
    confianca: float = Field(default=0.0, ge=0.0, le=1.0, description="Confiança da extração (0 a 1)")


class Cobertura(BaseModel):
    nome: str
    descricao: str | None = None
    sublimite: str | None = None
    pagina: int | None = None
    trecho: str | None = None
    confianca: float = Field(default=0.0, ge=0.0, le=1.0)


class Franquia(BaseModel):
    tipo: str
    valor: str | None = None
    descricao: str | None = None
    pagina: int | None = None
    trecho: str | None = None


class Exclusao(BaseModel):
    titulo: str
    descricao: str | None = None
    pagina: int | None = None
    trecho: str | None = None


class ApoliceDO(BaseModel):
    """Esquema canônico de uma apólice D&O extraída por LLM.

    O prompt de extração instrui o modelo a mapear sinônimos de seguradoras para estes
    campos canônicos, preservando o nome original encontrado no texto quando relevante.
    """

    # Identificação
    seguradora: Campo[str] = Field(default_factory=Campo)
    numero_apolice: Campo[str] = Field(default_factory=Campo)
    numero_processo_susep: Campo[str] = Field(default_factory=Campo)
    segurado: Campo[str] = Field(default_factory=Campo)
    vigencia_inicio: Campo[date] = Field(default_factory=Campo)
    vigencia_fim: Campo[date] = Field(default_factory=Campo)
    data_emissao: Campo[date] = Field(default_factory=Campo)

    # Valores
    lmg_apolice: Campo[float] = Field(default_factory=Campo)
    lmg_sinistro: Campo[float] = Field(default_factory=Campo)
    premio_total: Campo[float] = Field(default_factory=Campo)
    moeda: Campo[str] = Field(default_factory=Campo)

    # Coberturas e franquias
    coberturas: list[Cobertura] = Field(default_factory=list)
    franquias: list[Franquia] = Field(default_factory=list)
    custos_defesa_dentro_limite: Campo[bool] = Field(default_factory=Campo)

    # Condições temporais
    retroatividade: Campo[date] = Field(default_factory=Campo)
    prazo_complementar_notificacao: Campo[str] = Field(default_factory=Campo)
    base_cobertura: Campo[str] = Field(default_factory=Campo)
    prazo_aviso_sinistro: Campo[str] = Field(default_factory=Campo)

    # Exclusões
    exclusoes: list[Exclusao] = Field(default_factory=list)

    # Outros
    jurisdicao: Campo[str] = Field(default_factory=Campo)
    territorialidade: Campo[str] = Field(default_factory=Campo)
    observacoes: str | None = None


class StatusDiferenca(str, Enum):
    IGUAL = "igual"
    DIFERENTE = "diferente"
    SOMENTE_EM_A = "somente_em_A"
    SOMENTE_EM_B = "somente_em_B"


class Impacto(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"


class Citacao(BaseModel):
    pagina: int | None = None
    trecho: str | None = None


class Diferenca(BaseModel):
    categoria: str
    item: str
    valor_a: str | None = None
    valor_b: str | None = None
    status: StatusDiferenca
    impacto: Impacto
    explicacao: str
    citacao_a: Citacao | None = None
    citacao_b: Citacao | None = None


class ResultadoComparacao(BaseModel):
    apolice_a_id: int
    apolice_b_id: int
    diferencas: list[Diferenca]
    resumo_executivo: str | None = None
