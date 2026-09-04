from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

# Importa as funções de coleta do seu script coleta.py
from coleta import buscar_dolar, buscar_scfi_exemplo

# --- 1. ROTINA DE COLETA RECORRENTE ---
def rotina_coleta_semanal():
    data_hoje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n⏰ [{data_hoje}] Executando coleta automática agendada...")
    
    cotacao_usd = buscar_dolar()
    dados_frete = buscar_scfi_exemplo()
    
    novo_registro = pd.DataFrame([{
        "Data": dados_frete["data"],
        "USD_BRL": cotacao_usd,
        "SCFI_Geral": dados_frete["scfi_composite"],
        "SCFI_America_Sul": dados_frete["scfi_south_america"]
    }])
    
    # Anexa o registro ao histórico em CSV
    novo_registro.to_csv("dados_mercado.csv", mode='a', header=False, index=False)
    print("✅ Histórico em 'dados_mercado.csv' atualizado automaticamente!")

# --- 2. CONFIGURAÇÃO DO AGENDADOR NO CICLO DE VIDA DA API ---
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código executado ao LIGAR o servidor FastAPI
    scheduler.add_job(
        rotina_coleta_semanal,
        trigger=CronTrigger(day_of_week='fri', hour=18, minute=0),
        id='coleta_semanal_job',
        replace_existing=True
    )
    scheduler.start()
    print("🚀 BackgroundScheduler iniciado: Coleta agendada para toda sexta-feira às 18:00.")
    
    yield  # A aplicação roda normalmente aqui
    
    # Código executado ao DESLIGAR o servidor FastAPI
    scheduler.shutdown()
    print("🛑 BackgroundScheduler encerrado.")

# --- 3. INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(
    title="API de Previsão de Frete Marítimo",
    description="Servidor de IA com agendador de coleta automática integrado.",
    version="2.0",
    lifespan=lifespan
)

# Carrega o modelo treinado
model = joblib.load('modelo_frete.pkl')

class DadosMercado(BaseModel):
    scfi: float = 2140.5
    bunker: float = 620.0
    blank_sailings: float = 0.145
    usd_brl: float = 5.45
    scfi_var_1w: float = 0.032
    bunker_var_1w: float = -0.005
    usd_brl_var_1w: float = 0.012

@app.get("/")
def home():
    return {"status": "online", "agendador_ativo": scheduler.running}

@app.post("/prever")
def prever_tendencia(dados: DadosMercado):
    input_df = pd.DataFrame([{
        'scfi': dados.scfi,
        'bunker': dados.bunker,
        'blank_sailings': dados.blank_sailings,
        'usd_brl': dados.usd_brl,
        'scfi_var_1w': dados.scfi_var_1w,
        'bunker_var_1w': dados.bunker_var_1w,
        'usd_brl_var_1w': dados.usd_brl_var_1w
    }])
    
    predicao = model.predict(input_df)[0]
    probabilidades = model.predict_proba(input_df)[0]
    
    if predicao == 1:
        sinal = "BULLISH"
        label = "Previsão de Alta"
        confianca = probabilidades[1]
    else:
        sinal = "BEARISH"
        label = "Previsão de Baixa"
        confianca = probabilidades[0]
        
    return {
        "sinal": sinal,
        "label": label,
        "confianca_percentual": f"{round(confianca * 100, 1)}%",
        "dados_recebidos": dados.dict()
    }