from alerts import Alert
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime
import pandas as pd
import numpy as np


IBGE_CITY_CODES: dict[str, str] = {
    "3106200": "Belo Horizonte",
    "3304557": "Rio de Janeiro",
    "3509502": "São Paulo",
    "2927408": "Salvador",  
    "5300108": "Brasília",
}


class Predictor:
    def __init__(self, tablepath: str) -> None:
        self.tablepath = tablepath

    def _load_data(self, city_code: str) -> pd.DataFrame:
        if city_code not in IBGE_CITY_CODES:
            raise ValueError("City code not found in IBGE city codes.")
        
        result: pd.DataFrame = pd.read_csv(self.tablepath, sep=";")
        result = result[result["municipality_code_ibge"] == int(city_code)]
        result = result.sort_values(by=["year", "month"])
        
        return result

    def get_cases_history(self, city_code: str) -> pd.DataFrame:
        df = self._load_data(city_code)
        return df[["year", "month", "dengue_cases"]]

    def predict_outbreak(self, city_code: str, year: str, month: str) -> Alert:
        if int(year) < datetime.now().year or (int(year) == datetime.now().year and int(month) < datetime.now().month):
            raise ValueError("Cannot predict for past dates.")
        
        df = self._load_data(city_code)
        
        # CORREÇÃO 1: Filtrar apenas dados históricos confiáveis (até 2024)
        # Remove dados de 2025 que possuem valores climáticos artificiais
        df_train = df[df["year"] <= 2024].copy()
        
        # Criar feature de casos futuros (target)
        df_train["future_cases"] = df_train.groupby("municipality_code_ibge")["dengue_cases"].shift(-1)
        df_train = df_train.dropna()
        
        # CORREÇÃO 2: Adicionar features temporais
        df_train["month_sin"] = np.sin(2 * np.pi * df_train["month"] / 12)
        df_train["month_cos"] = np.cos(2 * np.pi * df_train["month"] / 12)
        
        # Features de entrada
        feature_cols = [
            'dengue_cases',
            'estimated_population',
            'rainfall_mm',
            'average_humidity',
            'average_temperature',
            'month_sin',
            'month_cos'
        ]
        
        X = df_train[feature_cols]
        y = df_train["future_cases"]
        
        # CORREÇÃO 3: Dividir em treino e teste para validação
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # CORREÇÃO 4: Normalizar features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Treinar modelo
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Avaliar modelo
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n=== Métricas do Modelo ===")
        print(f"MAE: {mae:.2f} casos")
        print(f"R²: {r2:.4f}")
        
        # CORREÇÃO 5: Preparar input para predição futura
        future_month = int(month)
        
        # Usar apenas dados históricos reais do mês correspondente (2015-2024)
        historical_month = df_train[df_train["month"] == future_month]
        
        # Se não houver dados suficientes, usar últimos 12 meses
        if len(historical_month) < 3:
            historical_month = df_train.tail(12)
        
        # CORREÇÃO 6: Usar caso mais recente como base + médias climáticas do mês
        latest_data = df_train.iloc[-1]
        
        future_input = {
            'dengue_cases': latest_data["dengue_cases"],  # Casos recentes
            'estimated_population': latest_data["estimated_population"],
            'rainfall_mm': historical_month["rainfall_mm"].median(),
            'average_humidity': historical_month["average_humidity"].median(),
            'average_temperature': historical_month["average_temperature"].median(),
            'month_sin': np.sin(2 * np.pi * future_month / 12),
            'month_cos': np.cos(2 * np.pi * future_month / 12)
        }
        
        X_future = pd.DataFrame([future_input])
        X_future_scaled = scaler.transform(X_future)
        
        predicted_cases = int(model.predict(X_future_scaled)[0])
        
        # Garantir que previsão não seja negativa
        predicted_cases = max(0, predicted_cases)
        
        # Classificação de severidade
        if predicted_cases > 1000:
            severity = "Severe"
        elif predicted_cases > 500:
            severity = "Moderate"
        else:
            severity = "Minor"
        
        alert = Alert(
            event="Dengue",
            severity=severity,
            certainly=f"MAE: {mae:.0f} casos, R²: {r2:.3f}",
            year=year,
            month=month,
            predicted_cases=predicted_cases,
            city_name=IBGE_CITY_CODES[city_code],
            city_code=city_code
        )
        
        return alert