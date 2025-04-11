
import streamlit as st
import pandas as pd
from ofxparse import OfxParser
from io import StringIO

st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("📊 Controle Financeiro - WebApp Simples")

# Upload do arquivo OFX
uploaded_file = st.file_uploader("📂 Faça o upload do extrato (.ofx)", type=["ofx"])

if uploaded_file is not None:
    ofx = OfxParser.parse(uploaded_file)
    transactions = ofx.account.statement.transactions

    # Transformar em DataFrame
    data = {
        "Data": [t.date for t in transactions],
        "Descrição": [t.payee for t in transactions],
        "Valor": [t.amount for t in transactions]
    }
    df = pd.DataFrame(data)

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
