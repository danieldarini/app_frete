import pandas as pd
import numpy as np
from datetime import datetime

# Gera as últimas 12 sextas-feiras
datas = pd.date_range(end=datetime.now(), periods=12, freq='W-FRI')

# Dados simulados com variações realistas de mercado
dados = {
    "Data": datas.strftime("%Y-%m-%d %H:%M:%S"),
    "USD_BRL": np.round(np.random.uniform(5.25, 5.55, size=12), 2),
    "SCFI_Geral": np.round(np.random.uniform(1950.0, 2180.0, size=12), 1),
    "SCFI_America_Sul": np.round(np.random.uniform(2050.0, 2350.0, size=12), 1)
}

df = pd.DataFrame(dados)
df.to_csv("dados_mercado.csv", index=False)
print("✅ Arquivo 'dados_mercado.csv' gerado com sucesso!")