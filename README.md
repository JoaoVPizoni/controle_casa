# Controle Financeiro Casinha

Aplicativo simples em Streamlit para registrar gastos domésticos por categoria e visualizar a evolução do orçamento.

## Estrutura do projeto

- `app.py` - ponto de entrada para o Streamlit (renderiza a UI usando o pacote `controle_financeiro`).
- `controle_financeiro/` - pacote com camada de dados, regras de negócio e visualização.
- `data/finances.db` - banco de dados SQLite onde os gastos e categorias são salvos.
- `requirements.txt` - dependências para rodar o projeto.

## Como rodar

1. (Opcional) Crie um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:

```bash
streamlit run app.py
```

## Funcionalidades

- Cadastro de categorias personalizadas.
- Registro de gastos vinculado a categorias.
- Visualização de gastos por categoria e evolução mensal.
- Persistência local em SQLite para manter os dados entre execuções.
- Backup/restauração do banco (`finances.db`) diretamente pela interface do Streamlit.
