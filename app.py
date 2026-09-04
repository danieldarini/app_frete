import os
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Previsão de Frete Marítimo", page_icon="🚢", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/prever")

st.title("🚢 Previsão de Tendência de Frete Marítimo")
st.subheader("América do Sul (ECSA / WCSA)")

# Inicialização limpa de Session State com chaves idênticas aos widgets
if 'scfi' not in st.session_state:
    st.session_state['scfi'] = 2140.50
if 'scfi_var' not in st.session_state:
    st.session_state['scfi_var'] = 3.20
if 'bunker' not in st.session_state:
    st.session_state['bunker'] = 620.00
if 'bunker_var' not in st.session_state:
    st.session_state['bunker_var'] = -0.50
if 'blank_sailings' not in st.session_state:
    st.session_state['blank_sailings'] = 0.14
if 'usd_brl' not in st.session_state:
    st.session_state['usd_brl'] = 5.45
if 'usd_brl_var' not in st.session_state:
    st.session_state['usd_brl_var'] = 1.20

# --- BOTÃO DE BUSCA EM TEMPO REAL ---
if st.button("🔄 Buscar Indicadores em Tempo Real", key="btn_atualizar"):
    with st.spinner("Atualizando dados via API..."):
        try:
            url_indicadores = API_URL.replace("/prever", "/indicadores")
            res = requests.get(url_indicadores, timeout=10)
            
            if res.status_code == 200:
                dados = res.json()
                st.session_state['scfi'] = float(dados["scfi"])
                st.session_state['scfi_var'] = float(dados["scfi_var_1w"])
                st.session_state['bunker'] = float(dados["bunker"])
                st.session_state['bunker_var'] = float(dados["bunker_var_1w"])
                st.session_state['blank_sailings'] = float(dados["blank_sailings"])
                st.session_state['usd_brl'] = float(dados["usd_brl"])
                st.session_state['usd_brl_var'] = float(dados["usd_brl_var_1w"])
                st.toast(f"Dólar atualizado ao vivo: R$ {dados['usd_brl']} ({dados['usd_brl_var_1w']}%)")
                st.rerun()
            else:
                st.error("Erro ao obter dados do servidor.")
        except Exception as e:
            st.error("Falha de conexão com a API.")

st.divider()

# --- FORMULÁRIO COM BINDING DIRETO DE KEY ---
col1, col2, col3 = st.columns(3)

with col1:
    scfi = st.number_input("Índice SCFI Atual (USD/TEU)", step=10.0, key="scfi")
    scfi_var = st.number_input("Variação Semanal SCFI (%)", key="scfi_var") / 100

with col2:
    bunker = st.number_input("Combustível VLSFO (USD/Ton)", step=5.0, key="bunker")
    bunker_var = st.number_input("Variação Semanal Bunker (%)", key="bunker_var") / 100

with col3:
    blank_sailings = st.slider("Taxa de Cancelamento (Blank Sailings)", 0.0, 0.5, step=0.005, key="blank_sailings")
    usd_brl = st.number_input("Cotação Dólar (USD/BRL)", step=0.01, key="usd_brl")
    usd_brl_var = st.number_input("Variação Semanal Câmbio (%)", key="usd_brl_var") / 100

st.divider()

# --- PREVISÃO ---
if st.button("🚀 Calcular Previsão de Frete", type="primary", key="btn_calcular"):
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
            st.warning("Erro de comunicação com a API.")
    except Exception:
        st.error("Servidor indisponível.")

# --- HISTÓRICO ---
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
    except Exception:
        st.info("Aguardando histórico.")