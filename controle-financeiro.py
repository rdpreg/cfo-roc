import streamlit as st
import pandas as pd

st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("📊 Controle Financeiro - WebApp com CSV")

def extrair_nome(descricao):
    try:
        partes = descricao.split(" - ")
        if len(partes) >= 2:
            nome = partes[1].strip()
            return nome.title()
    except:
        pass
    return "Não identificado"

def classificar_plano(valor):
    if valor == 250:
        return "Mensal"
    elif valor == 600:
        return "Trimestral"
    elif valor == 50:
        return "Avulso Ex-Aluno"
    elif valor == 80:
        return "Experiência"
    else:
        return "Outros"

uploaded_file = st.file_uploader("📂 Faça o upload do extrato (.csv)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    colunas_map = {
        "Data": "Data",
        "data": "Data",
        "Valor": "Valor",
        "valor": "Valor",
        "Descrição": "Descrição",
        "descricao": "Descrição"
    }
    df = df.rename(columns={col: colunas_map[col] for col in df.columns if col in colunas_map})

    colunas_esperadas = ["Data", "Descrição", "Valor"]
    if not all(col in df.columns for col in colunas_esperadas):
        st.error("❌ O CSV precisa conter as colunas: Data, Descrição, Valor")
        st.stop()

    df_receitas = df[df["Valor"] > 0].copy()
    df_receitas["Data"] = pd.to_datetime(df_receitas["Data"], dayfirst=True)
    df_receitas["Ano-Mês"] = df_receitas["Data"].dt.to_period("M").astype(str)
    df_receitas["Aluno"] = df_receitas["Descrição"].apply(extrair_nome)
    df_receitas["Plano"] = df_receitas["Valor"].apply(classificar_plano)

    meses_disponiveis = sorted(df_receitas["Ano-Mês"].unique(), reverse=True)
    mes_selecionado = st.selectbox("📅 Selecione o mês para o relatório", meses_disponiveis)

    df_mes = df_receitas[df_receitas["Ano-Mês"] == mes_selecionado].copy()
    df_mes["Validar"] = True  # valor padrão: todos validados

    st.subheader("✅ Valide os pagamentos do mês")
    df_editado = st.data_editor(
        df_mes[["Data", "Aluno", "Valor", "Plano", "Descrição", "Validar"]],
        use_container_width=True,
        num_rows="dynamic",
        key="validacao_pagamentos"
    )

    df_validados = df_editado[df_editado["Validar"] == True]

    # Relatório com base nos validados
    total_recebido = df_validados["Valor"].sum()

    total_por_plano = df_validados.groupby("Plano").agg({
        "Valor": "sum",
        "Aluno": "count"
    }).reset_index().rename(columns={"Aluno": "Qtd Pagamentos"})

    st.markdown(f"## 🧾 Relatório do mês: {mes_selecionado}")
    st.metric("💰 Total Recebido (validados)", f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.subheader("📌 Total por tipo de plano")
    st.dataframe(total_por_plano, use_container_width=True)

    st.subheader("📋 Pagamentos por Aluno, Mês e Plano (todos)")
    df_agrupado = df_receitas.groupby(["Ano-Mês", "Aluno", "Plano"])["Valor"].sum().reset_index()
    st.dataframe(df_agrupado, use_container_width=True)

    csv = df_agrupado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV dos pagamentos", csv, "pagamentos_agrupados.csv", "text/csv")
