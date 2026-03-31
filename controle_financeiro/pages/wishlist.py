"""Página da Lista de Desejos."""

from datetime import date

import pandas as pd
import streamlit as st

from .. import services


def render_wish_list_page(df: pd.DataFrame) -> None:
    """Renderiza a página da lista de desejos."""

    st.subheader("🎁 Lista de Desejos")
    st.write("Adicione itens que você deseja comprar no futuro.")

    with st.expander("Novo item de desejo", expanded=True):
        nome = st.text_input("Nome do item", key="nome_wish")
        preco = st.number_input("Preço (R$)", min_value=0.0, step=1.0, format="%.2f", key="preco_wish")
        link = st.text_input("Link (opcional)", key="link_wish")

        if st.button("Adicionar item", key="btn_adicionar_wish"):
            if not nome.strip() or preco <= 0:
                st.error("Preencha o nome e informe um preço maior que zero.")
            else:
                services.adicionar_wish_item(nome, preco, link)
                st.success("Item adicionado à lista de desejos.")
                st.rerun()

    df_wish = services.listar_wish_items_dataframe()
    if df_wish.empty:
        st.info("Nenhum item na lista de desejos ainda.")
        return

    st.dataframe(df_wish.drop(columns=["id"]), use_container_width=True)

    st.markdown("---")
    st.subheader("🛒 Selecionar item (comprar)")

    wish_options = [f"{row.id} — {row.nome} — R$ {row.preco:,.2f}" for row in df_wish.itertuples()]
    selected_wish = st.selectbox("Selecione o item para comprar", wish_options, key="selecionar_wish")

    nomes_categorias = [c.nome for c in services.get_categoria_choices()]
    categoria_compra = st.selectbox("Categoria da compra", nomes_categorias, key="categoria_compra")
    data_compra = st.date_input("Data da compra", value=date.today(), key="data_compra")

    if st.button("Confirmar compra", key="btn_confirmar_compra"):
        wish_id = int(selected_wish.split(" — ")[0])
        categoria_id = next(c.id for c in services.get_categoria_choices() if c.nome == categoria_compra)
        services.selecionar_wish_item(wish_id, categoria_id, data_compra)
        st.success("Item comprado e adicionado aos gastos!")
        st.rerun()

    if st.button("Limpar lista de desejos"):
        for row in df_wish.itertuples():
            services.remover_wish_item(row.id)
        st.success("Lista de desejos limpa.")
        st.rerun()