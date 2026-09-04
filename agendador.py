from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from coleta import buscar_dolar, buscar_scfi_exemplo
import pandas as pd

def rotina_coleta_semanal():
    data_hoje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n⏰ [{data_hoje}] Executando rotina agendada de coleta...")
    
    # 1. Executa os scrapers
    cotacao_usd = buscar_dolar()
    dados_frete = buscar_scfi_exemplo()
    
    # 2. Estrutura os novos dados
    novo_registro = pd.DataFrame([{
        "Data": dados_frete["data"],
        "USD_BRL": cotacao_usd,
        "SCFI_Geral": dados_frete["scfi_composite"],
        "SCFI_America_Sul": dados_frete["scfi_south_america"]
    }])
    
    # 3. Anexa ao histórico sem sobrescrever os dados antigos (mode='a')
    novo_registro.to_csv("dados_mercado.csv", mode='a', header=False, index=False)
    print("✅ Dados coletados e anexados ao arquivo 'dados_mercado.csv' com sucesso!")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Agenda a execução para toda sexta-feira (day_of_week='fri') às 18:00
    scheduler.add_job(
        rotina_coleta_semanal,
        trigger=CronTrigger(day_of_week='fri', hour=18, minute=0),
        id='coleta_frete_semanal',
        name='Coleta semanal de SCFI e Câmbio',
        replace_existing=True
    )
    
    print("🚀 Agendador ativo! O script rodará automaticamente toda sexta-feira às 18:00.")
    print("Pressione Ctrl + C para encerrar o agendador.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nAgendador encerrado.")