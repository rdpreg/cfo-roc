import streamlit as st
import pandas as pd

st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("📊 Controle Financeiro - WebApp com CSV")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("📂 Faça o upload do extrato (.csv)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Renomear colunas para facilitar o tratamento
    colunas_map = {
        "Data": "Data",
        "data": "Data",
        "Valor": "Valor",
        "valor": "Valor",
        "Descrição": "Descrição",
        "descricao": "Descrição"
    }
    df = df.rename(columns={col: colunas_map[col] for col in df.columns if col in colunas_map})

    # Verificar se as colunas esperadas estão presentes
    colunas_esperadas = ["Data", "Descrição", "Valor"]
    if not all(col in df.columns for col in colunas_esperadas):
        st.error("❌ O CSV precisa conter as colunas: Data, Descrição, Valor")
        st.stop()

    # Filtrar apenas receitas (valores positivos)
    df_receitas = df[df["Valor"] > 0].copy()

    # Converter datas e extrair mês/ano
    df_receitas["Data"] = pd.to_datetime(df_receitas["Data"])
    df_receitas["Ano-Mês"] = df_receitas["Data"].dt.to_period("M").astype(str)

    # Soma por mês
    receita_mensal = df_receitas.groupby("Ano-Mês")["Valor"].sum().reset_index()

    # Exibir os dados
    st.subheader("📅 Transações de Receita")
    st.dataframe(df_receitas, use_container_width=True)

    st.subheader("📈 Receita Mensal")
    st.bar_chart(receita_mensal.set_index("Ano-Mês"))

    # Download do CSV com os dados processados
    csv = df_receitas.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV das receitas", csv, "receitas.csv", "text/csv")
