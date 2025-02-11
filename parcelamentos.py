import streamlit as st
import pandas as pd
import json
import datetime

# Arquivo JSON para armazenar os dados
FILE_PATH = "parcelamentos.json"

# Carregar dados salvos
def carregar_dados():
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Salvar dados no arquivo JSON
def salvar_dados(dados):
    with open(FILE_PATH, "w") as file:
        json.dump(dados, file, indent=4)

# Inicializar os dados
parcelamentos = carregar_dados()

# Título do app
st.title("📌 Monitoramento de Parcelamentos")

# Formulário para adicionar novo parcelamento
st.subheader("Novo Parcelamento")
with st.form("form_parcelamento"):
    cliente = st.text_input("Nome do Cliente")
    tipo = st.selectbox("Tipo de Parcelamento", ["Sefaz", "Prefeitura", "DAU", "RFB"])
    observacoes = st.text_area("Observações")
    vencimento = st.number_input("Dia de Vencimento", min_value=1, max_value=31, step=1)
    parcelas_total = st.number_input("Quantidade de Parcelas", min_value=1, step=1)
    data_primeira = st.date_input("Data da 1ª Parcela", datetime.date.today())
    
    # Calcular a data da última parcela automaticamente
    data_ultima = data_primeira + pd.DateOffset(months=parcelas_total - 1)
    
    if st.form_submit_button("Adicionar Parcelamento"):
        novo_parcelamento = {
            "cliente": cliente,
            "tipo": tipo,
            "observacoes": observacoes,
            "vencimento": vencimento,
            "parcelas_total": parcelas_total,
            "data_primeira": str(data_primeira),
            "data_ultima": str(data_ultima),
            "status": "Enviado",  # Padrão inicial
        }
        parcelamentos.append(novo_parcelamento)
        salvar_dados(parcelamentos)
        st.success("Parcelamento adicionado com sucesso!")
        st.rerun()

# Exibição da lista de parcelamentos
st.subheader("📋 Lista de Parcelamentos")

if parcelamentos:
    df = pd.DataFrame(parcelamentos)
    
    # Calcular a parcela atual e parcelas em atraso
    hoje = datetime.date.today()
    df["data_primeira"] = pd.to_datetime(df["data_primeira"])
    df["data_ultima"] = pd.to_datetime(df["data_ultima"])

    df["parcela_atual"] = ((hoje.year - df["data_primeira"].dt.year) * 12 +
                           (hoje.month - df["data_primeira"].dt.month) + 1)

    df["parcela_atual"] = df["parcela_atual"].clip(lower=1, upper=df["parcelas_total"])

    df["parcelas_atraso"] = df["parcela_atual"] - (hoje.year - df["data_primeira"].dt.year) * 12 - (hoje.month - df["data_primeira"].dt.month)

    df["parcelas_atraso"] = df["parcelas_atraso"].apply(lambda x: x if x > 0 else 0)

    # Seleção de status
    status_opcoes = ["Baixado", "Enviado", "Encerrado"]
    df["status"] = df["status"].astype(str)

    # Criar colunas editáveis para o status
    for i in range(len(df)):
        df.at[i, "status"] = st.selectbox(f"Status ({df.at[i, 'cliente']})", status_opcoes, index=status_opcoes.index(df.at[i, "status"]), key=f"status_{i}")

    # Mostrar a tabela formatada
    st.dataframe(df[["cliente", "tipo", "vencimento", "parcelas_total", "parcela_atual", "parcelas_atraso", "status"]])

    # Atualizar os dados no JSON após alterações no status
    if st.button("Salvar Alterações"):
        for i in range(len(df)):
            parcelamentos[i]["status"] = df.at[i, "status"]
        salvar_dados(parcelamentos)
        st.success("Alterações salvas!")
        st.rerun()
else:
    st.info("Nenhum parcelamento cadastrado ainda.")
