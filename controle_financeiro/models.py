"""Modelos de domínio para o Controle Financeiro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Categoria:
    id: int
    nome: str


@dataclass(frozen=True)
class Gasto:
    id: int
    item: str
    categoria: str
    valor: float
    data_registro: date
