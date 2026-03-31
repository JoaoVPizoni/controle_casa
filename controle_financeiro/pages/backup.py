"""Página de Backup."""

import streamlit as st

from .. import services


def render_backup_page() -> None:
    """Renderiza a página de backup e restauração do banco de dados."""

    st.subheader("💾 Backup e restauração")
    st.write(
        "Faça download do arquivo `finances.db` para manter um backup e envie um arquivo .db para recuperar o histórico." 
        "Ao restaurar, os dados atuais serão substituídos."
    )

    data = services.exportar_banco()
    st.download_button(
        "Baixar backup",
        data,
        file_name="finances.db",
        mime="application/x-sqlite3",
    )

    st.markdown("---")
    st.write("**Restaurar banco de dados**")

    uploaded = st.file_uploader("Escolha um arquivo .db", type=["db"], key="upload_db")
    if uploaded is not None:
        services.importar_banco(uploaded.read())
        st.success("Banco de dados restaurado com sucesso. Recarregando...")
        st.rerun()