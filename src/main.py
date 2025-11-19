from predictor import Predictor, IBGE_CITY_CODES
from alerts import Alert
import pandas as pd


def print_next_predictions(city_code: str):
    print("\n--- Next Predictions ---\n")
    A: Alert = P.predict_outbreak(city_code, year="2025", month="11")
    print(F"(2025/11): {A.predicted_cases} casos | Risco: {A.severity}")
    A: Alert = P.predict_outbreak(city_code, year="2025", month="12")
    print(F"(2025/12): {A.predicted_cases} casos | Risco: {A.severity}")
    for i in range(1, 13):
        B: Alert = P.predict_outbreak(city_code, year="2026", month=str(i))
        print(F"(2026/{str(i).zfill(2)}): {B.predicted_cases} casos | Risco: {B.severity}")


def print_data(city_code: str):
    # pd.set_option('display.max_rows', None)
    print("\n", f"{IBGE_CITY_CODES[city_code]} " ,"="*40,"\n", sep="")
    history: pd.DataFrame = P.get_cases_history(city_code)
    print(history)
    print_next_predictions(city_code)


if __name__ == "__main__":

    GHOST_TABLE: str = ".\\data\\ghost_table.csv"
    MASTER_TABLE: str = ".\\data\\master_table.csv"

    P = Predictor(tablepath=MASTER_TABLE)

    print_data(city_code="3106200")  # Belo Horizonte"
    print_data(city_code="3118601")  # Contagem"
    print_data(city_code="3127701")  # Governador Valadares"
    print_data(city_code="3136702")  # Juiz de Fora"
    print_data(city_code="3143302")  # Montes Claros"
    print_data(city_code="3154606")  # Ribeirão das Neves"
    print_data(city_code="3170107")  # Uberaba"
    print_data(city_code="3170206")  # Uberlândia"
