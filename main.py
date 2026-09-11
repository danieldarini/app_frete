import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="API de Previsão de Frete Marítimo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputPrevisao(BaseModel):
    scfi: float
    scfi_var_1w: float
    scfi_geral_pontos: float
    scfi_geral_var_1w: float
    bunker: float
    bunker_var_1w: float
    blank_sailings: float
    usd_brl: float
    usd_brl_var_1w: float

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/indicadores")
def obter_indicadores():
    headers = {"User-Agent": "Mozilla/5.0"}
    usd_brl = 5.10
    usd_brl_var = 0.85

    try:
        res_usd = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL", headers=headers, timeout=5)
        if res_usd.status_code == 200:
            dados = res_usd.json().get("USDBRL", {})
            usd_brl = round(float(dados.get("bid")), 2)
            usd_brl_var = round(float(dados.get("pctChange")), 2)
    except Exception as e:
        print(f"Erro ao buscar Dólar: {e}")

    return {
        "scfi_geral_pontos": 3590.05,
        "scfi_geral_var_1w": 1.85,
        "scfi": 7805.00,
        "scfi_var_1w": 2.45,
        "bunker": 638.50,
        "bunker_var_1w": 1.10,
        "blank_sailings": 0.12,
        "usd_brl": usd_brl,
        "usd_brl_var_1w": usd_brl_var
    }

@app.post("/prever")
def prever_frete(dados: InputPrevisao):
    # Score ponderado: Rota Local (30%), SCFI Global (15%), Bunker (25%), Dólar (15%), Blank Sailings (15%)
    score = (
        (dados.scfi_var_1w * 0.30) +
        (dados.scfi_geral_var_1w * 0.15) +
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