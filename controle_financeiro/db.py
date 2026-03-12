"""Camada de dados: persistência usando SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .config import DB_PATH, DATA_DIR

SQL_CREATE_CATEGORIES = """
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);
"""

SQL_CREATE_GASTOS = """
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    valor REAL NOT NULL,
    data_registro TEXT NOT NULL,
    FOREIGN KEY(categoria_id) REFERENCES categorias(id)
);
"""

SQL_INSERT_CATEGORIA = "INSERT OR IGNORE INTO categorias (nome) VALUES (?);"
SQL_SELECT_CATEGORIAS = "SELECT id, nome FROM categorias ORDER BY nome;"

SQL_INSERT_GASTO = "INSERT INTO gastos (item, categoria_id, valor, data_registro) VALUES (?, ?, ?, ?);"
SQL_SELECT_GASTOS = """
SELECT
  g.id,
  g.item,
  c.nome AS categoria,
  g.valor,
  g.data_registro
FROM gastos g
JOIN categorias c ON c.id = g.categoria_id
ORDER BY g.data_registro DESC, g.id DESC;
"""

SQL_DELETE_GASTOS = "DELETE FROM gastos;"
SQL_DELETE_GASTO_BY_ID = "DELETE FROM gastos WHERE id = ?;"


def _ensure_db_path() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Retorna conexão com o banco de dados local.

    Garante que o arquivo e as tabelas existam.
    """

    _ensure_db_path()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    with conn:
        conn.execute(SQL_CREATE_CATEGORIES)
        conn.execute(SQL_CREATE_GASTOS)

    return conn


def ensure_default_categories(categories: Iterable[str]) -> None:
    """Garante que as categorias base existam no banco."""

    conn = get_connection()
    with conn:
        conn.executemany(SQL_INSERT_CATEGORIA, ((c,) for c in categories))


def list_categories() -> List[Tuple[int, str]]:
    """Retorna todas as categorias (id, nome)."""

    conn = get_connection()
    cur = conn.execute(SQL_SELECT_CATEGORIAS)
    return [(row[0], row[1]) for row in cur.fetchall()]


def add_category(name: str) -> int:
    """Adiciona uma categoria e retorna seu ID."""

    conn = get_connection()
    with conn:
        cur = conn.execute(SQL_INSERT_CATEGORIA, (name.strip(),))
        return cur.lastrowid


def add_expense(item: str, categoria_id: int, valor: float, data_registro: str) -> int:
    """Adiciona um gasto e retorna seu ID."""

    conn = get_connection()
    with conn:
        cur = conn.execute(SQL_INSERT_GASTO, (item.strip(), categoria_id, valor, data_registro))
        return cur.lastrowid


def list_expenses() -> List[sqlite3.Row]:
    """Retorna a lista de gastos ordenada por data de registro."""

    conn = get_connection()
    cur = conn.execute(SQL_SELECT_GASTOS)
    return cur.fetchall()


def clear_expenses() -> None:
    """Remove todos os gastos armazenados."""

    conn = get_connection()
    with conn:
        conn.execute(SQL_DELETE_GASTOS)


def delete_expense(expense_id: int) -> None:
    """Remove um gasto específico pelo ID."""

    conn = get_connection()
    with conn:
        conn.execute(SQL_DELETE_GASTO_BY_ID, (expense_id,)) 

