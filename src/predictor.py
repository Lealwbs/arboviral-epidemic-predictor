from alerts import Alert # Local import
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from datetime import datetime
import pandas as pd
import numpy as np


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
        
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        result: pd.DataFrame = pd.read_csv(self.tablepath, sep=";")
        result = result[result["municipality_code_ibge"] == int(city_code)]
        result = result.sort_values(by=["year", "month"])

        return result

    
    def get_cases_history(self, city_code: str) -> pd.DataFrame:
        df = self._load_data(city_code)
        return df[["year", "month", "dengue_cases"]]


    def _make_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona lags, rolling means e codificação de mês.
        df must contain columns: year(int), month(int), dengue_cases, rainfall_mm, average_humidity, average_temperature, estimated_population
        """
        df = df.copy().reset_index(drop=True)
        # ensure month/year ints
        df["month"] = df["month"].astype(int)
        df["year"] = df["year"].astype(int)

        # lags of cases (t, t-1, t-2)
        df["lag_1_cases"] = df["dengue_cases"].shift(1)
        df["lag_2_cases"] = df["dengue_cases"].shift(2)
        df["lag_3_cases"] = df["dengue_cases"].shift(3)

        # rolling means of last 3 months of cases
        df["roll_3_cases"] = df["dengue_cases"].rolling(window=3, min_periods=1).mean().shift(1)

        # seasonal encoding: month as cyclic features (helps RF sometimes)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        # drop rows with NaN created by shifts
        df = df.dropna(subset=["lag_1_cases"])

        return df

    def predict_outbreak(self, city_code: str, year: str, month: str) -> Alert:
        # validation
        if int(year) < datetime.now().year or (int(year) == datetime.now().year and int(month) < datetime.now().month):
            raise ValueError("Cannot predict for past dates.")
        # load and prepare
        df_raw = self._load_data(city_code)  # includes many years
        # sort by time
        df_raw = df_raw.sort_values(["year", "month"]).reset_index(drop=True)

        # create future target (cases next month) using original series
        df = df_raw.copy()
        df["future_cases"] = df["dengue_cases"].shift(-1)  # predict next month
        # drop last row where future_cases == NaN
        df = df.dropna(subset=["future_cases"])

        # create features including lags and seasonal encodings
        df_feat = self._make_time_features(df)

        feature_cols = [
            "lag_1_cases", "lag_2_cases", "lag_3_cases", "roll_3_cases",
            "estimated_population", "rainfall_mm", "average_humidity", "average_temperature",
            "month_sin", "month_cos"
        ]

        X = df_feat[feature_cols]
        y = df_feat["future_cases"]

        # stabilize target: log1p (optional but helps with big outliers)
        use_log = True
        if use_log:
            y_train = np.log1p(y)
        else:
            y_train = y

        # temporal split for validation (not strictly necessary for final model, but good to evaluate)
        tscv = TimeSeriesSplit(n_splits=3)
        maes = []
        for train_idx, val_idx in tscv.split(X):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

            m = RandomForestRegressor(n_estimators=200, random_state=42)
            m.fit(X_tr, y_tr)
            pred = m.predict(X_val)
            if use_log:
                pred = np.expm1(pred)
                yv = np.expm1(y_val)
            else:
                yv = y_val
            maes.append(mean_absolute_error(yv, pred))
        # optional: print validation MAE
        # print("TimeSeries MAE (cv):", np.mean(maes))

        # train final model on all data
        model = RandomForestRegressor(n_estimators=300, random_state=42)
        model.fit(X, y_train)

        # === build X_future using last known row(s) ===
        last_row = df_raw.sort_values(["year", "month"]).iloc[-1]  # last observed month in raw data
        # compute lags for future: lag_1 is last_row.dengue_cases, lag_2 is previous, etc.
        # get previous 3 dengue_cases
        last_three = df_raw.sort_values(["year", "month"])["dengue_cases"].values[-3:]
        lag_1 = float(last_three[-1]) if len(last_three) >= 1 else float(last_row["dengue_cases"])
        lag_2 = float(last_three[-2]) if len(last_three) >= 2 else lag_1
        lag_3 = float(last_three[-3]) if len(last_three) >= 3 else lag_2
        roll_3 = np.mean(last_three) if len(last_three) > 0 else lag_1

        # seasonal climate: use historical same-month averages from raw data (not from df after shifting)
        fm = int(month)
        season_rows = df_raw[df_raw["month"] == fm]
        if len(season_rows) < 3:
            # fallback to last year's month if not enough data
            season_rows = df_raw

        est_pop = season_rows["estimated_population"].mean()
        rain = season_rows["rainfall_mm"].mean()
        hum = season_rows["average_humidity"].mean()
        temp = season_rows["average_temperature"].mean()

        month_sin = np.sin(2 * np.pi * fm / 12)
        month_cos = np.cos(2 * np.pi * fm / 12)

        X_future = pd.DataFrame([{
            "lag_1_cases": lag_1,
            "lag_2_cases": lag_2,
            "lag_3_cases": lag_3,
            "roll_3_cases": roll_3,
            "estimated_population": est_pop,
            "rainfall_mm": rain,
            "average_humidity": hum,
            "average_temperature": temp,
            "month_sin": month_sin,
            "month_cos": month_cos
        }])

        # predict and inverse transform
        pred_raw = model.predict(X_future)[0]
        if use_log:
            predicted_cases = int(max(0, np.expm1(pred_raw)))
        else:
            predicted_cases = int(max(0, pred_raw))

        # severity mapping (tune thresholds as needed)
        if predicted_cases > 10000:
            severity = "Extreme"
        elif predicted_cases > 3000:
            severity = "Severe"
        elif predicted_cases > 1000:
            severity = "Moderate"
        else:
            severity = "Minor"

        alert = Alert(
            event="Dengue",
            severity=severity,
            certainly="Alta, baseada no modelo de previsão Random Forest",
            year=year,
            month=month,
            predicted_cases=predicted_cases,
            city_name=IBGE_CITY_CODES[city_code],
            city_code=city_code
        )

        return alert