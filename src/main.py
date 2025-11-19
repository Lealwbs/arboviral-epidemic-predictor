from predictor import Predictor
from alerts import Alert
import pandas as pd

if __name__ == "__main__":

    GHOST_TABLE: str = ".\\data\\ghost_table.csv"
    MASTER_TABLE: str = ".\\data\\master_table.csv"

    P = Predictor(tablepath=MASTER_TABLE)


    history: pd.DataFrame = P.get_cases_history(city_code="3106200")
    pd.set_option('display.max_rows', None)
    print(history)

    print("\n--- Next Predictions ---\n")
    A: Alert = P.predict_outbreak(city_code="3106200", year="2025", month="12")    # Belo Horizonte
    print("Year: 2025", "Month: 2025", A.predicted_cases)
    for i in range(1, 13):
        B: Alert = P.predict_outbreak(city_code="3106200", year="2026", month=str(i))    # Belo Horizonte
        print("Year: 2026", "Month:", str(i).zfill(2), B.predicted_cases)

