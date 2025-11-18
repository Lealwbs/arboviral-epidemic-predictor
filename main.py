import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("#" * 48)
print("# All the packages were imported with success! #")
print("#" * 48, "\n")

def main():

    table_path: str = "files\\tabela_ghost.csv"
    df: pd.DataFrame = pd.read_csv(table_path, sep=";")

    # Criando variável-alvo com shift de 1 mês
    df["future_cases"] = df.groupby("municipality_code_ibge")["total_cases"].shift(-1)
    df = df.dropna() # Remove missing values (NaN or None) from the DataFrame.

    X = df[[
        'rainfall_mm',
        'average_humidity',
        'average_temperature',
        'dengue_cases',
        'chikungunya_cases',
        'zika_cases',
        'total_cases',
        'estimated_population',
        ]]    

    y = df['future_cases']

    # pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # print(df)
    # print(X)
    # print(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #print(X_train, X_test, y_train, y_test)

    modelo = RandomForestRegressor(n_estimators=300)
    modelo.fit(X_train, y_train)

    previsoes = modelo.predict(X_test)
    # print(previsoes)
    erro = mean_absolute_error(y_test, previsoes)

    print("Mean Absolute Error:", erro)

    print()
    print("#" * 48)
    print("# The program was executed successfully!       #")
    print("#" * 48)



if __name__ == "__main__":
    main()
    # Missão: tentar prever Dezembro / o ano de 2026
    

