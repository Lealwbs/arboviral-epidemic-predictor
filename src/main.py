from predictor import Predictor
from alerts import Alert


if __name__ == "__main__":

    GHOST_TABLE: str = ".\\data\\ghost_table.csv"
    MASTER_TABLE: str = ".\\data\\master_table.csv"
    
    P = Predictor(tablepath=MASTER_TABLE)

    A: Alert = P.predict_outbreak(city_code="3106200", year="2025", month="12")    # Belo Horizonte

    print(A)

