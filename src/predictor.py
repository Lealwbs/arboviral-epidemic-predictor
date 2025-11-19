from alerts import Alert
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime
import pandas as pd
import numpy as np


IBGE_CITY_CODES: dict[str, str] = {
    "1100205": "Porto Velho",
    "1302603": "Manaus",
    "1501402": "Belém",
    "2111300": "São Luís",
    "2211001": "Teresina",
    "2304400": "Fortaleza",
    "2408102": "Natal",
    "2504009": "Campina Grande",
    "2507507": "João Pessoa",
    "2611606": "Recife",
    "2704302": "Maceió",
    "2800308": "Aracaju",
    "2905701": "Camaçari",
    "2910800": "Feira de Santana",
    "2927408": "Salvador",
    "3106200": "Belo Horizonte",
    "3136702": "Juiz de Fora",
    "3143302": "Montes Claros",
    "3170206": "Uberlândia",
    "3304557": "Rio de Janeiro",
    "3304904": "São Gonçalo",
    "3518800": "Guarulhos",
    "3552205": "Sorocaba",
    "4106902": "Curitiba",
    "4113700": "Londrina",
    "4115200": "Maringá",
    "4205407": "Florianópolis",
    "4305108": "Caxias do Sul",
    "4314902": "Porto Alegre",
    "5002704": "Campo Grande",
    "5103403": "Cuiabá",
    "5208707": "Goiânia",
    "5300108": "Brasília",
}

class Predictor:
    def __init__(self, tablepath: str) -> None:
        self.tablepath = tablepath
        self.model = None
        self.scaler = None

    def _load_data(self, city_code: str) -> pd.DataFrame:
        if city_code not in IBGE_CITY_CODES:
            raise ValueError("City code not found in IBGE city codes.")
        
        result: pd.DataFrame = pd.read_csv(self.tablepath, sep=";")
        result = result[result["municipality_code_ibge"] == int(city_code)]
        result = result.sort_values(by=["year", "month"])
        
        return result

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features engenheiradas para melhorar a predição"""
        df = df.copy()
        
        # Features temporais cíclicas (captura sazonalidade)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
        
        # Lag features (casos dos meses anteriores)
        df["cases_lag_1"] = df["dengue_cases"].shift(1)
        df["cases_lag_2"] = df["dengue_cases"].shift(2)
        df["cases_lag_3"] = df["dengue_cases"].shift(3)
        
        # Média móvel dos últimos 3 meses
        df["cases_rolling_3"] = df["dengue_cases"].rolling(window=3, min_periods=1).mean()
        
        # Média móvel dos últimos 6 meses
        df["cases_rolling_6"] = df["dengue_cases"].rolling(window=6, min_periods=1).mean()
        
        # Tendência (diferença em relação ao mês anterior)
        df["cases_diff"] = df["dengue_cases"].diff()
        
        # Features climáticas defasadas (clima do mês anterior influencia casos atuais)
        df["rainfall_lag_1"] = df["rainfall_mm"].shift(1)
        df["temp_lag_1"] = df["average_temperature"].shift(1)
        df["humidity_lag_1"] = df["average_humidity"].shift(1)
        
        # Interações entre variáveis climáticas
        df["temp_humidity"] = df["average_temperature"] * df["average_humidity"]
        df["rainfall_humidity"] = df["rainfall_mm"] * df["average_humidity"]
        
        return df

    def get_cases_history(self, city_code: str) -> pd.DataFrame:
        df = self._load_data(city_code)
        return df[["year", "month", "dengue_cases"]]

    def predict_outbreak(self, city_code: str, year: str, month: str) -> Alert:
        future_year = int(year)
        future_month = int(month)
        
        # Carregar todos os dados históricos
        df = self._load_data(city_code)
        
        # Criar features engenheiradas
        df = self._create_features(df)
        
        # Preparar dados para treinamento
        # Target: casos do próximo mês
        df["target"] = df["dengue_cases"].shift(-1)
        
        # Remover linhas com NaN (causadas por shift e rolling)
        df_clean = df.dropna().copy()
        
        # Definir features para o modelo
        feature_cols = [
            # Temporal
            'month_sin', 'month_cos',
            # Casos históricos
            'dengue_cases', 'cases_lag_1', 'cases_lag_2', 'cases_lag_3',
            'cases_rolling_3', 'cases_rolling_6', 'cases_diff',
            # Clima atual
            'rainfall_mm', 'average_temperature', 'average_humidity',
            # Clima defasado
            'rainfall_lag_1', 'temp_lag_1', 'humidity_lag_1',
            # Interações
            'temp_humidity', 'rainfall_humidity',
            # População
            'estimated_population'
        ]
        
        X = df_clean[feature_cols]
        y = df_clean["target"]
        
        # Dividir em treino (80%) e teste (20%) - últimos 20% para validação temporal
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Normalizar features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treinar modelo
        self.model = RandomForestRegressor(
            n_estimators=300,
            max_depth=20,
            min_samples_split=3,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Avaliar modelo
        y_pred_test = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred_test)
        r2 = r2_score(y_test, y_pred_test)
        
        # print(f"\n{'='*50}")
        # print(f"MÉTRICAS DO MODELO - {IBGE_CITY_CODES[city_code]}")
        # print(f"{'='*50}")
        # print(f"MAE (Erro Médio Absoluto): {mae:.2f} casos")
        # print(f"R² (Coeficiente de Determinação): {r2:.4f}")
        # print(f"Tamanho do treino: {len(X_train)} meses")
        # print(f"Tamanho do teste: {len(X_test)} meses")
        # print(f"{'='*50}\n")
        
        # ===== PREPARAR INPUT PARA PREVISÃO =====
        
        # Obter o último registro completo (mais recente)
        latest_complete = df.dropna().iloc[-1]
        
        # Calcular médias históricas do mês alvo (sazonalidade)
        historical_month = df[df["month"] == future_month]
        
        # Construir input para predição
        future_input = {
            # Temporal (mês alvo)
            'month_sin': np.sin(2 * np.pi * future_month / 12),
            'month_cos': np.cos(2 * np.pi * future_month / 12),
            
            # Casos mais recentes (usar últimos valores conhecidos)
            'dengue_cases': latest_complete["dengue_cases"],
            'cases_lag_1': latest_complete["dengue_cases"],
            'cases_lag_2': latest_complete["cases_lag_1"],
            'cases_lag_3': latest_complete["cases_lag_2"],
            'cases_rolling_3': latest_complete["cases_rolling_3"],
            'cases_rolling_6': latest_complete["cases_rolling_6"],
            'cases_diff': latest_complete["cases_diff"],
            
            # Clima (usar médias históricas do mês alvo)
            'rainfall_mm': historical_month["rainfall_mm"].median() if len(historical_month) > 0 
                          else df["rainfall_mm"].median(),
            'average_temperature': historical_month["average_temperature"].median() if len(historical_month) > 0 
                                  else df["average_temperature"].median(),
            'average_humidity': historical_month["average_humidity"].median() if len(historical_month) > 0 
                               else df["average_humidity"].median(),
            
            # Clima defasado
            'rainfall_lag_1': historical_month["rainfall_mm"].median() if len(historical_month) > 0 
                             else df["rainfall_mm"].median(),
            'temp_lag_1': historical_month["average_temperature"].median() if len(historical_month) > 0 
                         else df["average_temperature"].median(),
            'humidity_lag_1': historical_month["average_humidity"].median() if len(historical_month) > 0 
                             else df["average_humidity"].median(),
            
            # Interações (calcular com base nos valores acima)
            'temp_humidity': (historical_month["average_temperature"].median() if len(historical_month) > 0 
                             else df["average_temperature"].median()) * 
                            (historical_month["average_humidity"].median() if len(historical_month) > 0 
                             else df["average_humidity"].median()),
            'rainfall_humidity': (historical_month["rainfall_mm"].median() if len(historical_month) > 0 
                                 else df["rainfall_mm"].median()) * 
                                (historical_month["average_humidity"].median() if len(historical_month) > 0 
                                 else df["average_humidity"].median()),
            
            # População (usar mais recente)
            'estimated_population': latest_complete["estimated_population"]
        }
        
        # Criar DataFrame e normalizar
        X_future = pd.DataFrame([future_input])
        X_future_scaled = self.scaler.transform(X_future)
        
        # Fazer predição
        predicted_cases = int(self.model.predict(X_future_scaled)[0])
        
        # Garantir que não seja negativo
        predicted_cases = max(0, predicted_cases)
        
        # Classificação de severidade baseada nos dados históricos do município
        # Calcula percentis dos casos históricos
        historical_cases = df["dengue_cases"].dropna()
        p50 = historical_cases.quantile(0.50) 
        p80 = historical_cases.quantile(0.80)  
        
        # Classificação adaptativa
        if predicted_cases > p80:
            severity = "Severe"  # Acima de 90% dos casos históricos
        elif predicted_cases > p50:
            severity = "Moderate"  # Entre 75% e 90%
        else:
            severity = "Minor"  # Abaixo de 75%
        
        print(f"Thresholds calculados para {IBGE_CITY_CODES[city_code]}:")
        print(f"  Minor: < {p50:.0f} casos (até 50º percentil)")
        print(f"  Moderate: {p50:.0f} - {p80:.0f} casos (50º-80º percentil)")
        print(f"  Severe: > {p80:.0f} casos (acima 80º percentil)")
        print(f"  Previsão: {predicted_cases} casos → {severity}\n")
        
        # Criar alerta
        alert = Alert(
            event="Dengue",
            severity=severity,
            certainly=f"Confiança: MAE={mae:.0f} casos, R²={r2:.3f}",
            year=year,
            month=month,
            predicted_cases=predicted_cases,
            city_name=IBGE_CITY_CODES[city_code],
            city_code=city_code
        )
        
        return alert