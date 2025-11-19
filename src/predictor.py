from alerts import Alert # Local import
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from datetime import datetime
import pandas as pd


IBGE_CITY_CODES: dict[str:str] = {
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
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

        return result[result["municipality_code_ibge"] == int(city_code)]

    
    def predict_outbreak(self, city_code: str, year: str, month: str) -> Alert:
        if int(year) < datetime.now().year or (int(year) == datetime.now().year and int(month) < datetime.now().month):
            raise ValueError("Cannot predict for past dates.")
        
        df = self._load_data(city_code)
        X_COMPONENTS = df[[
            'dengue_cases',
            'estimated_population',
            'rainfall_mm',
            'average_humidity',
            'average_temperature',
            ]] 
        
        # print(df)
        
        result: Alert = Alert(
            # event="Dengue",
            # severity="Alto Risco",
            # certainly="100%",
            # year="2024",
            # month="06",
            # city_name="Belo Horizonte",
            # city_code="3106200"
        )

        return result

    #     # Criando variável-alvo com shift de 1 mês
    #     df["future_cases"] = df.groupby("municipality_code_ibge")["total_cases"].shift(-1)
    #     df = df.dropna() # Remove missing values (NaN or None) from the DataFrame.
   
    #     y = df['future_cases']

    #     X_train, X_test, y_train, y_test = train_test_split(X_COMPONENTS, y, test_size=0.2, random_state=42)


    #     modelo = RandomForestRegressor(n_estimators=300)
    #     modelo.fit(X_train, y_train)

    #     previsoes = modelo.predict(X_test)
    #     erro = mean_absolute_error(y_test, previsoes)

    #     print("Mean Absolute Error:", erro)