"""Camada de dados: persistência usando SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .config import DB_PATH, DATA_DIR

SQL_CREATE_RENDAS = """
CREATE TABLE IF NOT EXISTS rendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa TEXT NOT NULL,
    valor REAL NOT NULL,
    data_registro TEXT NOT NULL
);
"""

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

SQL_CREATE_WISH_ITEMS = """
CREATE TABLE IF NOT EXISTS wish_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    link TEXT
);
"""

SQL_INSERT_RENDA = "INSERT INTO rendas (pessoa, valor, data_registro) VALUES (?, ?, ?);"
SQL_SELECT_RENDAS = "SELECT id, pessoa, valor, data_registro FROM rendas ORDER BY data_registro DESC, id DESC;"

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

SQL_INSERT_WISH_ITEM = "INSERT INTO wish_items (nome, preco, link) VALUES (?, ?, ?);"
SQL_SELECT_WISH_ITEMS = "SELECT id, nome, preco, link FROM wish_items ORDER BY id DESC;"
SQL_DELETE_WISH_ITEM_BY_ID = "DELETE FROM wish_items WHERE id = ?;"


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
        conn.execute(SQL_CREATE_RENDAS)
        conn.execute(SQL_CREATE_WISH_ITEMS)

    return conn


def get_db_path() -> Path:
    """Retorna o caminho para o arquivo de banco de dados."""

    _ensure_db_path()
    return DB_PATH


def export_db() -> bytes:
    """Exporta o arquivo de banco de dados para bytes."""

    # Garantir que o arquivo exista e a estrutura esteja criada.
    conn = get_connection()
    conn.close()
    return DB_PATH.read_bytes()


def import_db(data: bytes) -> None:
    """Substitui o banco de dados atual pelo arquivo enviado."""

    _ensure_db_path()
    # Fecha qualquer conexão aberta antes de sobrescrever o arquivo.
    sqlite3.connect(DB_PATH).close()
    DB_PATH.write_bytes(data)


def ensure_default_categories(categories: Iterable[str]) -> None:
    """Garante que as categorias base existam no banco."""

    conn = get_connection()
    with conn:
        conn.executemany(SQL_INSERT_CATEGORIA, ((c,) for c in categories))


def list_categories() -> List[Tuple[int, str]]:
    """Retorna todas as categorias (id, nome)."""

    with get_connection() as conn:
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

    with get_connection() as conn:
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


def add_income(pessoa: str, valor: float, data_registro: str) -> int:
    """Adiciona uma renda e retorna seu ID."""

    conn = get_connection()
    with conn:
        cur = conn.execute(SQL_INSERT_RENDA, (pessoa.strip(), valor, data_registro))
        return cur.lastrowid


def list_incomes() -> List[sqlite3.Row]:
    """Retorna a lista de rendas ordenada por data de registro."""

    with get_connection() as conn:
        cur = conn.execute(SQL_SELECT_RENDAS)
        return cur.fetchall()


def clear_incomes() -> None:
    """Remove todas as rendas armazenadas."""

    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM rendas;")


def delete_income(income_id: int) -> None:
    """Remove uma renda específica pelo ID."""

    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM rendas WHERE id = ?;", (income_id,))


def add_wish_item(nome: str, preco: float, link: str) -> int:
    """Adiciona um item de desejo e retorna seu ID."""

    conn = get_connection()
    with conn:
        cur = conn.execute(SQL_INSERT_WISH_ITEM, (nome.strip(), preco, link.strip() if link else ""))
        return cur.lastrowid


def list_wish_items() -> List[sqlite3.Row]:
    """Retorna a lista de itens de desejo."""

    with get_connection() as conn:
        cur = conn.execute(SQL_SELECT_WISH_ITEMS)
        return cur.fetchall()


def delete_wish_item(wish_item_id: int) -> None:
    """Remove um item de desejo específico pelo ID."""

    conn = get_connection()
    with conn:
        conn.execute(SQL_DELETE_WISH_ITEM_BY_ID, (wish_item_id,)) 

