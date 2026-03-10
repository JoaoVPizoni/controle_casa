"""Configurações compartilhadas do projeto."""

from pathlib import Path

# Base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Local onde o banco de dados será persistido
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "finances.db"

# Categorias iniciais que aparecem na primeira execução
DEFAULT_CATEGORIES = [
    "Sala",
    "Cozinha",
    "Quarto",
    "Escritório",
    "Banheiro"
]
