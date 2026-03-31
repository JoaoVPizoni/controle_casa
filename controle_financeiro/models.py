"""Modelos de domínio para o Controle Financeiro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Renda:
    id: int
    pessoa: str
    valor: float
    data_registro: date


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


@dataclass(frozen=True)
class WishItem:
    id: int
    nome: str
    preco: float
    link: str
