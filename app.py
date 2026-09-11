import os
import requests
import streamlit as st

st.set_page_config(page_title="Previsão de Frete Marítimo", page_icon="🚢", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/prever")

st.title("🚢 Previsão de Tendência de Frete Marítimo")
st.subheader("América do Sul (ECSA / WCSA)")

# Inicialização do Session State
if 'val_scfi_geral' not in st.session_state:
    st.session_state['val_scfi_geral'] = 3590.05
if 'val_scfi_geral_var' not in st.session_state:
    st.session_state['val_scfi_geral_var'] = 1.85
if 'val_scfi' not in st.session_state:
    st.session_state['val_scfi'] = 7805.00
if 'val_scfi_var' not in st.session_state:
    st.session_state['val_scfi_var'] = 2.45
if 'val_bunker' not in st.session_state:
    st.session_state['val_bunker'] = 638.50
if 'val_bunker_var' not in st.session_state:
    st.session_state['val_bunker_var'] = 1.10
if 'val_blank_sailings' not in st.session_state:
    st.session_state['val_blank_sailings'] = 0.120
if 'val_usd_brl' not in st.session_state:
    st.session_state['val_usd_brl'] = 5.10
if 'val_usd_brl_var' not in st.session_state:
    st.session_state['val_usd_brl_var'] = 0.85
if 'val_usd_cma_cgm' not in st.session_state:
    st.session_state['val_usd_cma_cgm'] = 5.55

# --- BOTÃO DE ATUALIZAÇÃO VIA API ---
if st.button("🔄 Buscar Indicadores em Tempo Real", key="btn_atualizar_indicadores"):
    with st.spinner("Conectando à API e atualizando mercado..."):
        try:
            url_indicadores = API_URL.replace("/prever", "/indicadores")
            res = requests.get(url_indicadores, timeout=10)
            
            if res.status_code == 200:
                dados = res.json()
                st.session_state['val_scfi_geral'] = float(dados.get("scfi_geral_pontos", 3590.05))
                st.session_state['val_scfi_geral_var'] = float(dados.get("scfi_geral_var_1w", 1.85))
                st.session_state['val_scfi'] = float(dados["scfi"])
                st.session_state['val_scfi_var'] = float(dados["scfi_var_1w"])
                st.session_state['val_bunker'] = float(dados["bunker"])
                st.session_state['val_bunker_var'] = float(dados["bunker_var_1w"])
                st.session_state['val_blank_sailings'] = float(dados["blank_sailings"])
                st.session_state['val_usd_brl'] = float(dados["usd_brl"])
                st.session_state['val_usd_brl_var'] = float(dados["usd_brl_var_1w"])
                st.session_state['val_usd_cma_cgm'] = float(dados.get("usd_cma_cgm", 5.55))
                
                st.toast("✅ Indicadores atualizados (incluindo Dólar Armador CMA CGM)!")
                st.rerun()
            else:
                st.error("Servidor backend indisponível.")
        except Exception:
            st.error("Erro de conexão com a API de indicadores.")

st.divider()

# --- CARTOES DE DESTAQUE CAMBIAL ---
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("Dólar PTAX / Comercial (DUIMP)", f"R$ {st.session_state['val_usd_brl']:.2f}")
with col_m2:
    st.metric(
        "Dólar Armador (CMA CGM)", 
        f"R$ {st.session_state['val_usd_cma_cgm']:.2f}",
        help="Taxa do dia para pagamento de frete/THC cobrada pela CMA CGM Brasil"
    )

st.divider()

# --- FORMULÁRIO ---
scfi_geral = st.number_input("Índice SCFI Geral (Pontos)", value=st.session_state['val_scfi_geral'], step=10.0)
scfi_geral_var = st.number_input("Variação Semanal SCFI Geral (%)", value=st.session_state['val_scfi_geral_var']) / 100

scfi = st.number_input("Índice SCFI Atual - Rota América do Sul (USD/TEU)", value=st.session_state['val_scfi'], step=50.0)
scfi_var = st.number_input("Variação Semanal SCFI Rota Local (%)", value=st.session_state['val_scfi_var']) / 100

bunker = st.number_input("Combustível VLSFO (USD/Ton)", value=st.session_state['val_bunker'], step=5.0)
bunker_var = st.number_input("Variação Semanal Bunker (%)", value=st.session_state['val_bunker_var']) / 100

blank_sailings = st.slider("Taxa de Cancelamento (Blank Sailings)", 0.0, 0.5, value=st.session_state['val_blank_sailings'], step=0.005)
usd_brl = st.number_input("Cotação Dólar Comercial / DUIMP (USD/BRL)", value=st.session_state['val_usd_brl'], step=0.01)
usd_brl_var = st.number_input("Variação Semanal Câmbio (%)", value=st.session_state['val_usd_brl_var']) / 100
usd_cma_cgm = st.number_input("Dólar Armador CMA CGM (USD/BRL)", value=st.session_state['val_usd_cma_cgm'], step=0.01)

st.divider()

# --- PREVISÃO ---
if st.button("🚀 Calcular Previsão de Frete", type="primary", key="btn_calcular"):
    payload = {
        "scfi": scfi,
        "scfi_var_1w": scfi_var,
        "scfi_geral_pontos": scfi_geral,
        "scfi_geral_var_1w": scfi_geral_var,
        "bunker": bunker,
        "bunker_var_1w": bunker_var,
        "blank_sailings": blank_sailings,
        "usd_brl": usd_brl,
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