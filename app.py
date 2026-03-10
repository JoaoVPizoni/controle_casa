"""Ponto de entrada do aplicativo Streamlit.

Este arquivo permanece pequeno e delega a lógica para o pacote
`controle_financeiro`, que gerencia dados, categorias e visualização.
"""

from controle_financeiro import run_app


if __name__ == "__main__":
    run_app()
