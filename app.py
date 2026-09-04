import os
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Previsão de Frete Marítimo", page_icon="🚢", layout="wide")

# Detecta automaticamente a URL da API (Ambiente de Produção ou Localhost)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/prever")

st.title("🚢 Previsão de Tendência de Frete Marítimo")
st.subheader("América do Sul (ECSA / WCSA)")

# --- FUNÇÃO DE BUSCA EM TEMPO REAL ---
def buscar_dolar_ao_vivo():
    try:
        url = "https://www.google.com/finance/quote/USD-BRL"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            price_div = soup.find("div", {"class": "YMlKec fxKbKc"})
            if price_div:
                return float(price_div.text.strip().replace(",", "."))
    except Exception:
        pass
    return 5.45

# --- ESTADO INICIAL DOS CAMPOS ---
if 'usd_brl' not in st.session_state:
    st.session_state.usd_brl = 5.45
if 'scfi' not in st.session_state:
    st.session_state.scfi = 2140.50

if st.button("🔄 Buscar Indicadores em Tempo Real"):
    with st.spinner("Consultando cotação de mercado..."):
        cotacao = buscar_dolar_ao_vivo()
        st.session_state.usd_brl = cotacao
        st.success("Dados atualizados com sucesso!")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    scfi = st.number_input("Índice SCFI Atual (USD/TEU)", value=st.session_state.scfi, step=10.0)
    scfi_var = st.number_input("Variação Semanal SCFI (%)", value=3.20) / 100

with col2:
    bunker = st.number_input("Combustível VLSFO (USD/Ton)", value=620.00, step=5.0)
    bunker_var = st.number_input("Variação Semanal Bunker (%)", value=-0.50) / 100

with col3:
    blank_sailings = st.slider("Taxa de Cancelamento (Blank Sailings)", 0.0, 0.5, 0.14, 0.005)
    usd_brl = st.number_input("Cotação Dólar (USD/BRL)", value=st.session_state.usd_brl, step=0.01)
    usd_brl_var = st.number_input("Variação Semanal Câmbio (%)", value=1.20) / 100

st.divider()

if st.button("🚀 Calcular Previsão de Frete", type="primary"):
    payload = {
        "scfi": scfi,
        "bunker": bunker,
        "blank_sailings": blank_sailings,
        "usd_brl": usd_brl,
        "scfi_var_1w": scfi_var,
        "bunker_var_1w": bunker_var,
        "usd_brl_var_1w": usd_brl_var
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            resultado = response.json()
            st.markdown("### Resultado da Análise da IA")
            
            if resultado["sinal"] == "BULLISH":
                st.error(f"🔴 **{resultado['label'].upper()}** — Tendência de Aumento do Frete (D+14 dias)")
            else:
                st.success(f"🟢 **{resultado['label'].upper()}** — Tendência de Queda do Frete (D+14 dias)")
                
            st.metric("Confiança do Modelo", resultado["confianca_percentual"])
        else:
            st.warning("Erro de comunicação com a API de produção.")
            
    except Exception as e:
        st.error(f"Não foi possível conectar à API em `{API_URL}`. Verifique se o servidor está online.")

# --- VISUALIZAÇÃO DE HISTÓRICO ---
st.divider()
st.subheader("📈 Histórico do Mercado (SCFI & Câmbio)")

if os.path.exists("dados_mercado.csv"):
    try:
        df_hist = pd.read_csv("dados_mercado.csv")
        df_hist["Data"] = pd.to_datetime(df_hist["Data"])
        
        tab1, tab2 = st.tabs(["Índice SCFI", "Dólar (USD/BRL)"])
        
        with tab1:
            st.line_chart(df_hist.set_index("Data")[["SCFI_Geral", "SCFI_America_Sul"]])
            
        with tab2:
            st.line_chart(df_hist.set_index("Data")["USD_BRL"])
            
    except Exception as e:
        st.info("Aguardando estrutura válida no arquivo de histórico para gerar os gráficos.")
else:
    st.info("Nenhum histórico registrado ainda. O agendador criará o arquivo 'dados_mercado.csv' automaticamente na primeira coleta.")