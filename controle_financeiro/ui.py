"""Interface Streamlit para o Controle Financeiro."""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from . import config
from . import services


def _render_sidebar(df: pd.DataFrame) -> None:
    """Renderiza o painel lateral com formulários de entrada."""

    st.sidebar.header("📥 Adicionar")

    with st.sidebar.expander("Nova categoria", expanded=False):
        nome_nova = st.text_input("Nome da categoria", key="nova_categoria")
        if st.button("Criar categoria", key="btn_criar_categoria"):
            if nome_nova.strip():
                services.adicionar_categoria(nome_nova)
                st.success(f"Categoria '{nome_nova}' adicionada.")
                st.rerun()
            else:
                st.error("Digite um nome de categoria válido.")

    with st.sidebar.expander("Novo gasto", expanded=True):
        nomes = [c.nome for c in services.get_categoria_choices()]
        categoria = st.selectbox("Categoria", nomes, key="categoria")
        item = st.text_input("Descrição do gasto", key="item")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0, format="%.2f", key="valor")
        data_registro = st.date_input("Data", value=date.today(), key="data_registro")

        if st.button("Adicionar gasto", key="btn_adicionar_gasto"):
            if not item.strip() or valor <= 0:
                st.error("Preencha a descrição e informe um valor maior que zero.")
            else:
                categoria_id = next(c.id for c in services.get_categoria_choices() if c.nome == categoria)
                services.adicionar_gasto(item, categoria_id, valor, data_registro)
                st.success("Gasto adicionado com sucesso.")
                st.rerun()

    if st.sidebar.button("Limpar todos os gastos"):
        services.limpar_gastos()
        st.rerun()

    if not df.empty:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🗑️ Remover gasto")

        despesas = df.sort_values(["data_registro", "id"], ascending=[False, False])
        opções = [f"{row.id} — {row.item} ({row.categoria}) — R$ {row.valor:,.2f}" for row in despesas.itertuples()]
        escolha = st.sidebar.selectbox("Selecione o gasto", opções, key="remover_gasto")

        if st.sidebar.button("Remover selecionado"):
            gasto_id = int(escolha.split(" — ")[0])
            services.remover_gasto(gasto_id)
            st.success("Gasto removido com sucesso.")
            st.rerun()


def _render_dashboard(df: pd.DataFrame) -> None:
    """Renderiza os painéis principais e gráficos."""

    st.subheader("📋 Gastos registrados")
    if df.empty:
        st.info("Nenhum gasto registrado ainda. Use o painel lateral para adicionar itens.")
        return

    total = services.calcular_total_geral(df)
    st.metric("Gasto total", f"R$ {total:,.2f}")

    st.dataframe(df.drop(columns=["id"]).assign(data_registro=lambda d: d["data_registro"].astype(str)), use_container_width=True)

    st.subheader("📊 Visão por categoria")
    total_por_categoria = services.calcular_total_por_categoria(df)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Tabela de gastos por categoria**")
        df_display = total_por_categoria.rename(columns={"categoria": "Categoria", "valor": "Total (R$)"})
        st.table(df_display.style.format({"Total (R$)": "{:.2f}"}))

    with col2:
        fig_pizza = px.pie(
            total_por_categoria,
            values="valor",
            names="categoria",
            title="Distribuição de gastos por categoria",
            hole=0.4,
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("📈 Evolução mensal")
    df_mes = df.copy()
    df_mes["mes"] = pd.to_datetime(df_mes["data_registro"]).dt.to_period("M")
    evolução = df_mes.groupby("mes")["valor"].sum().reset_index()
    evolução["mes"] = evolução["mes"].dt.to_timestamp()

    fig_linha = px.line(
        evolução,
        x="mes",
        y="valor",
        title="Gastos por mês",
        markers=True,
    )
    fig_linha.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)")
    st.plotly_chart(fig_linha, use_container_width=True)


def run_app() -> None:
    """Função principal para rodar a aplicação Streamlit."""

    st.set_page_config(page_title="Controle Financeiro Residencial", layout="wide")

    services.db.ensure_default_categories(config.DEFAULT_CATEGORIES)

    st.title("🏠 Controle Financeiro Residencial")
    st.caption("Organize seus gastos por área e acompanhe sua evolução financeira.")

    df = services.listar_gastos_dataframe()

    _render_sidebar(df)

    st.divider()
    _render_dashboard(df)

    st.markdown("---")
    st.caption(
        "Dica: este projeto salva seus dados localmente em `data/finances.db`." 
        "Para iniciar, execute: `streamlit run app.py`"
    )
