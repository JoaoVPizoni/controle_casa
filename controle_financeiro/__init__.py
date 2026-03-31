"""Pacote principal do Controle Financeiro Casinha.

Este pacote oferece camadas de dados, regras de negócio e UI para o aplicativo
Streamlit de controle de gastos.
"""

from __future__ import annotations

import streamlit as st

from . import config
from . import services
from .pages import backup, dashboard, wishlist


def run_app() -> None:
    """Função principal para rodar a aplicação Streamlit."""

    st.set_page_config(page_title="Controle Financeiro Residencial", layout="wide")

    services.db.ensure_default_categories(config.DEFAULT_CATEGORIES)

    st.title("🏠 Controle Financeiro Residencial")
    st.caption("Organize seus gastos por área e acompanhe sua evolução financeira.")

    df = services.listar_gastos_dataframe()
    df_rendas = services.listar_rendas_dataframe()

    page = st.sidebar.radio("Navegação", ["Dashboard", "Lista de Desejos", "Backup"], index=0, key="page_nav")

    if page == "Dashboard":
        dashboard.render_sidebar(df, df_rendas)
        st.divider()
        dashboard.render_dashboard(df, df_rendas)
    elif page == "Lista de Desejos":
        wishlist.render_wish_list_page(df)
    else:
        backup.render_backup_page()

    st.markdown("---")
    st.caption(
        "Dica: este projeto salva seus dados localmente em `data/finances.db`." 
        "Para iniciar, execute: `streamlit run app.py`"
    )


__all__ = ["run_app"]
