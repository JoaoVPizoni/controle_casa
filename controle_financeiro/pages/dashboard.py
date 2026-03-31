"""Página do Dashboard."""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from .. import services


def render_sidebar(df: pd.DataFrame, df_rendas: pd.DataFrame) -> None:
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

    with st.sidebar.expander("Nova renda", expanded=False):
        pessoa = st.text_input("Nome da pessoa", key="pessoa")
        valor_renda = st.number_input("Valor da renda (R$)", min_value=0.0, step=1.0, format="%.2f", key="valor_renda")
        data_renda = st.date_input("Data", value=date.today(), key="data_renda")

        if st.button("Adicionar renda", key="btn_adicionar_renda"):
            if not pessoa.strip() or valor_renda <= 0:
                st.error("Preencha o nome da pessoa e informe um valor maior que zero.")
            else:
                services.adicionar_renda(pessoa, valor_renda, data_renda)
                st.success("Renda adicionada com sucesso.")
                st.rerun()

    if st.sidebar.button("Limpar todos os gastos"):
        services.limpar_gastos()
        st.rerun()

    if st.sidebar.button("Limpar todas as rendas"):
        services.limpar_rendas()
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

    if not df_rendas.empty:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🗑️ Remover renda")

        rendas = df_rendas.sort_values(["data_registro", "id"], ascending=[False, False])
        opções_rendas = [f"{row.id} — {row.pessoa} — R$ {row.valor:,.2f}" for row in rendas.itertuples()]
        escolha_renda = st.sidebar.selectbox("Selecione a renda", opções_rendas, key="remover_renda")

        if st.sidebar.button("Remover selecionada"):
            renda_id = int(escolha_renda.split(" — ")[0])
            services.remover_renda(renda_id)
            st.success("Renda removida com sucesso.")
            st.rerun()


def render_dashboard(df: pd.DataFrame, df_rendas: pd.DataFrame) -> None:
    """Renderiza os painéis principais e gráficos."""

    df_rendas = services.listar_rendas_dataframe()

    st.subheader("📋 Gastos registrados")
    if df.empty:
        st.info("Nenhum gasto registrado ainda. Use o painel lateral para adicionar itens.")
        return

    total_gastos = services.calcular_total_geral(df)
    total_rendas = services.calcular_total_rendas(df_rendas)
    saldo = services.calcular_saldo(df, df_rendas)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de rendas", f"R$ {total_rendas:,.2f}")
    with col2:
        st.metric("Total de gastos", f"R$ {total_gastos:,.2f}")
    with col3:
        st.metric("Saldo restante", f"R$ {saldo:,.2f}")

    st.dataframe(df.drop(columns=["id"]).assign(data_registro=lambda d: d["data_registro"].astype(str)), use_container_width=True)

    st.subheader("💰 Rendas registradas")
    if df_rendas.empty:
        st.info("Nenhuma renda registrada ainda. Use o painel lateral para adicionar rendas.")
    else:
        st.dataframe(df_rendas.drop(columns=["id"]).assign(data_registro=lambda d: d["data_registro"].astype(str)), use_container_width=True)

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
    df_mes["mes"] = pd.to_datetime(df_mes["data_registro"]).dt.to_period("M").dt.to_timestamp()

    # Gráfico de barras empilhadas por categoria, mês a mês
    evolução_stack = (
        df_mes.groupby(["mes", "categoria"])["valor"]
        .sum()
        .reset_index()
    )

    fig_barras = px.bar(
        evolução_stack,
        x="mes",
        y="valor",
        color="categoria",
        title="Gastos por mês (empilhado por categoria)",
        labels={"valor": "Valor (R$)", "mes": "Mês", "categoria": "Categoria"},
        barmode="stack",
    )
    fig_barras.update_layout(xaxis_tickformat="%b %Y")
    st.plotly_chart(fig_barras, use_container_width=True)