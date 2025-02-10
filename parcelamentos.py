import streamlit as st
import pandas as pd
import json
import os

# Arquivo JSON para armazenar os parcelamentos
DATA_FILE = "parcelamentos.json"

# Função para carregar os parcelamentos salvos
def carregar_parcelamentos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Função para salvar os parcelamentos
def salvar_parcelamentos(parcelamentos):
    with open(DATA_FILE, "w") as f:
        json.dump(parcelamentos, f, indent=4)

# Carrega os dados existentes
parcelamentos = carregar_parcelamentos()

# Interface do Streamlit
st.title("📊 Monitoramento de Parcelamentos")

# Formulário de cadastro
st.header("Cadastrar Novo Parcelamento")

cliente = st.text_input("Nome do Cliente")
tipo_parcelamento = st.selectbox("Tipo de Parcelamento", ["Sefaz", "Prefeitura", "DAU", "RFB"])
observacoes = st.text_area("Observações")
data_vencimento = st.date_input("Data de Vencimento")
num_parcelas = st.number_input("Quantidade de Parcelas", min_value=1, step=1)
data_primeira = st.date_input("Data da 1ª Parcela")
data_ultima = st.date_input("Data da Última Parcela")

if st.button("Cadastrar Parcelamento"):
    if cliente and num_parcelas > 0:
        parcelamento = {
            "cliente": cliente,
            "tipo": tipo_parcelamento,
            "observacoes": observacoes,
            "data_vencimento": str(data_vencimento),
            "num_parcelas": num_parcelas,
            "data_primeira": str(data_primeira),
            "data_ultima": str(data_ultima)
        }
        parcelamentos.append(parcelamento)
        salvar_parcelamentos(parcelamentos)
        st.success("Parcelamento cadastrado com sucesso!")
        st.rerun()
    else:
        st.error("Preencha todos os campos corretamente.")

# Exibir tabela com parcelamentos cadastrados
st.header("📋 Parcelamentos Cadastrados")

# Filtro de busca
filtro_cliente = st.text_input("🔍 Buscar por Cliente")
filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos", "Sefaz", "Prefeitura", "DAU", "RFB"])

# Filtrar os dados conforme a busca
dados_filtrados = [
    p for p in parcelamentos
    if (filtro_cliente.lower() in p.get("cliente", "").lower()) and (filtro_tipo == "Todos" or p.get("tipo", "") == filtro_tipo)
]

# Exibir tabela
if dados_filtrados:
    df = pd.DataFrame(dados_filtrados)
    df = df.rename(columns={
        "cliente": "Cliente",
        "tipo": "Tipo",
        "observacoes": "Observações",
        "data_vencimento": "Vencimento",
        "num_parcelas": "Parcelas",
        "data_primeira": "1ª Parcela",
        "data_ultima": "Última Parcela"
    })
    st.dataframe(df)
else:
    st.info("Nenhum parcelamento encontrado.")