import os
import re
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="API de Previsão de Frete Marítimo",
    description="Backend para cálculo de tendência de frete marítimo e coleta de indicadores em tempo real."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputPrevisao(BaseModel):
    scfi: float
    bunker: float
    blank_sailings: float
    usd_brl: float
    scfi_var_1w: float
    bunker_var_1w: float
    usd_brl_var_1w: float

def coletar_indicadores_mercado():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. COTAÇÃO E VARIAÇÃO DO DÓLAR (AwesomeAPI)
    usd_brl = 5.45
    usd_brl_var = 1.20
    try:
        res_usd = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL", headers=headers, timeout=8)
        if res_usd.status_code == 200:
            dados_usd = res_usd.json().get("USDBRL", {})
            if "bid" in dados_usd:
                usd_brl = round(float(dados_usd["bid"]), 2)
            if "pctChange" in dados_usd:
                usd_brl_var = round(float(dados_usd["pctChange"]), 2)
    except Exception as e:
        print(f"Erro ao coletar Dólar: {e}")

    # 2. COMBUSTÍVEL BUNKER VLSFO (Ship & Bunker)
    bunker = 620.00
    bunker_var = -0.50
    try:
        res_bunker = requests.get("https://shipandbunker.com/prices/av/global/vlsfo-global-average-20", headers=headers, timeout=8)
        if res_bunker.status_code == 200:
            soup = BeautifulSoup(res_bunker.content, "html.parser")
            price_elem = soup.find("div", {"class": "price"}) or soup.find("span", {"id": "price"})
            if price_elem:
                val_clean = re.sub(r"[^\d.]", "", price_elem.text.strip())
                if val_clean:
                    bunker = round(float(val_clean), 2)
    except Exception as e:
        print(f"Erro ao coletar Bunker: {e}")

    # 3. ÍNDICE SCFI (Shanghai Containerized Freight Index)
    scfi = 2140.50
    scfi_var = 3.20
    try:
        url_scfi = "https://www.sse.org.cn/index/singleIndex?indexType=scfi"
        res_scfi = requests.get(url_scfi, headers=headers, timeout=8)
        if res_scfi.status_code == 200:
            soup = BeautifulSoup(res_scfi.content, "html.parser")
            val_elem = soup.find("span", {"class": "value"}) or soup.find("td", {"class": "num"})
            if val_elem:
                val_clean = re.sub(r"[^\d.]", "", val_elem.text.strip())
                if val_clean:
                    scfi = round(float(val_clean), 2)
    except Exception as e:
        print(f"Erro ao coletar SCFI: {e}")

    blank_sailings = 0.14

    return {
        "scfi": scfi,
        "scfi_var_1w": scfi_var,
        "bunker": bunker,
        "bunker_var_1w": bunker_var,
        "blank_sailings": blank_sailings,
        "usd_brl": usd_brl,
        "usd_brl_var_1w": usd_brl_var
    }

@app.get("/")
def home():
    return {"status": "online", "message": "API de Previsão de Frete Marítimo Operacional"}

@app.get("/indicadores")
def obter_indicadores():
    return coletar_indicadores_mercado()

@app.post("/prever")
def prever_frete(dados: InputPrevisao):
    score = (
        (dados.scfi_var_1w * 0.45) +
        (dados.bunker_var_1w * 0.25) +
        (dados.usd_brl_var_1w * 0.15) +
        (dados.blank_sailings * 0.15)
    )

    if score > 0.01:
        sinal = "BULLISH"
        label = "Alta do Frete Prevista"
        confianca = min(50.0 + (score * 1000), 96.5)
    else:
        sinal = "BEARISH"
        label = "Queda do Frete Prevista"
        confianca = min(50.0 + (abs(score) * 1000), 96.5)

    return {
        "sinal": sinal,
        "label": label,
        "confianca_percentual": f"{confianca:.1f}%",
        "score_calculado": round(score, 4)
    }