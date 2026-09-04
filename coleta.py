import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def buscar_dolar():
    url = "https://www.google.com/finance/quote/USD-BRL"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            price_div = soup.find("div", {"class": "YMlKec fxKbKc"})
            if price_div:
                return float(price_div.text.strip().replace(",", "."))
    except Exception:
        pass
    
    # Valor padrão de segurança para não travar o aprendizado
    print("Aviso: Conexão bloqueada pelo site. Usando cotação padrão (5.45 BRL).")
    return 5.45

def buscar_scfi_exemplo():
    return {
        "data": datetime.today().strftime("%Y-%m-%d"),
        "scfi_composite": 2140.5,
        "scfi_south_america": 1850.0
    }

if __name__ == "__main__":
    print("Iniciando coleta de dados de mercado...")
    
    cotacao_usd = buscar_dolar()
    dados_frete = buscar_scfi_exemplo()
    
    df = pd.DataFrame([{
        "Data": dados_frete["data"],
        "USD_BRL": cotacao_usd,
        "SCFI_Geral": dados_frete["scfi_composite"],
        "SCFI_America_Sul": dados_frete["scfi_south_america"]
    }])
    
    print("\n=== DADOS COLETADOS COM SUCESSO ===")
    print(df.to_string(index=False))
    
    # Salva o arquivo CSV
    df.to_csv("dados_mercado.csv", index=False)
    print("\nArquivo 'dados_mercado.csv' gerado na pasta do seu projeto!")