"""Regras de negócio e transformação de dados."""

from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd

from . import db
from .models import Categoria, Gasto


def get_categoria_choices() -> List[Categoria]:
    """Retorna todas as categorias disponíveis."""

    raw = db.list_categories()
    return [Categoria(id=row[0], nome=row[1]) for row in raw]


def adicionar_categoria(nome: str) -> Categoria:
    """Cria nova categoria ou retorna a já existente."""

    categoria_id = db.add_category(nome)
    return Categoria(id=categoria_id, nome=nome)


def adicionar_gasto(item: str, categoria_id: int, valor: float, data_registro: date) -> Gasto:
    """Registra um novo gasto."""

    gasto_id = db.add_expense(item, categoria_id, valor, data_registro.isoformat())
    return Gasto(id=gasto_id, item=item, categoria=next(c.nome for c in get_categoria_choices() if c.id == categoria_id), valor=valor, data_registro=data_registro)


def listar_gastos_dataframe() -> pd.DataFrame:
    """Retorna todos os gastos como DataFrame, incluindo categorias."""

    raw = db.list_expenses()
    df = pd.DataFrame(raw, columns=["id", "item", "categoria", "valor", "data_registro"])
    if not df.empty:
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date
    return df


def calcular_total_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa gastos por categoria para análise."""

    if df.empty:
        return df

    total_por_categoria = (
        df.groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

    total_por_categoria["valor"] = total_por_categoria["valor"].round(2)
    return total_por_categoria


def calcular_total_geral(df: pd.DataFrame) -> float:
    """Retorna o total de todos os gastos."""

    total = float(df["valor"].sum()) if not df.empty else 0.0
    return round(total, 2)


def limpar_gastos() -> None:
    """Limpa todos os gastos registrados."""

    db.clear_expenses()


def remover_gasto(gasto_id: int) -> None:
    """Remove um gasto existente pelo seu ID."""

    db.delete_expense(gasto_id)


def exportar_banco() -> bytes:
    """Exporta o banco de dados atual como um arquivo binário."""

    return db.export_db()


def importar_banco(data: bytes) -> None:
    """Substitui o banco de dados atual pelo arquivo enviado."""

    db.import_db(data)
