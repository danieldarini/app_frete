import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import joblib

print("Iniciando o treinamento da Inteligência Artificial...")

# 1. Simulação de histórico de 120 semanas de mercado para aprendizado do modelo
np.random.seed(42)
datas = pd.date_range(end=pd.Timestamp.now(), periods=120, freq='W')

scfi_hist = np.cumsum(np.random.normal(5, 35, 120)) + 1900
bunker_hist = np.cumsum(np.random.normal(1, 8, 120)) + 590
blank_sailings_hist = np.clip(np.random.normal(0.12, 0.03, 120), 0.02, 0.30)
usd_brl_hist = np.cumsum(np.random.normal(0.01, 0.03, 120)) + 5.10

df = pd.DataFrame({
    'scfi': scfi_hist,
    'bunker': bunker_hist,
    'blank_sailings': blank_sailings_hist,
    'usd_brl': usd_brl_hist
})

# 2. Definição da Meta (Target): 1 = Previsão de ALTA, 0 = Previsão de BAIXA
df['retorno_futuro'] = df['scfi'].pct_change(-2) * -1  # Projeção para 2 semanas à frente
df['target'] = (df['retorno_futuro'] > 0.015).astype(int)

# 3. Engenharia de Atributos (Features)
df['scfi_var_1w'] = df['scfi'].pct_change(1)
df['bunker_var_1w'] = df['bunker'].pct_change(1)
df['usd_brl_var_1w'] = df['usd_brl'].pct_change(1)

df_clean = df.dropna()

features = ['scfi', 'bunker', 'blank_sailings', 'usd_brl', 'scfi_var_1w', 'bunker_var_1w', 'usd_brl_var_1w']
X = df_clean[features]
y = df_clean['target']

# 4. Treinamento do Algoritmo
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, random_state=42)
model.fit(X, y)

# 5. Salvar o Modelo Treinado no arquivo .pkl
joblib.dump(model, 'modelo_frete.pkl')

print("\n=== MODELO TREINADO COM SUCESSO ===")
print("O arquivo 'modelo_frete.pkl' foi gerado na pasta do seu projeto!")