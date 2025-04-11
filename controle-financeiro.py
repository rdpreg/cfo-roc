import streamlit as st
import pandas as pd

st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("📊 Controle Financeiro - WebApp com CSV")

# Função para extrair nome do aluno da descrição
def extrair_nome(descricao):
    try:
        partes = descricao.split(" - ")
        if len(partes) >= 2:
            nome = partes[1].strip()
            return nome.title()
    except:
        pass
    return "Não identificado"

# Função para classificar o tipo de plano
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

    # Corrigir data e gerar campos auxiliares
    df_receitas["Data"] = pd.to_datetime(df_receitas["Data"], dayfirst=True)
    df_receitas["Ano-Mês"] = df_receitas["Data"].dt.to_period("M").astype(str)
    df_receitas["Aluno"] = df_receitas["Descrição"].apply(extrair_nome)
    df_receitas["Plano"] = df_receitas["Valor"].apply(classificar_plano)

    # Agrupar valores por mês, aluno e plano
    df_agrupado = df_receitas.groupby(["Ano-Mês", "Aluno", "Plano"])["Valor"].sum().reset_index()

    # Exibir a tabela
    st.subheader("📋 Pagamentos por Aluno, Mês e Plano")
    st.dataframe(df_agrupado, use_container_width=True)

    # Baixar CSV
    csv = df_agrupado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV dos pagamentos", csv, "pagamentos_agrupados.csv", "text/csv")
