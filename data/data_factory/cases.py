import pandas as pd
import requests
from datetime import datetime

# =============================
# CONFIGURAÇÕES
# =============================

CITIES = {
    "3106200": "Belo Horizonte",
    "3170206": "Uberlândia",
    "3118601": "Contagem",
    "3136702": "Juiz de Fora",
    "3143302": "Montes Claros",
    "3170107": "Uberaba",
    "3154606": "Ribeirão das Neves",
    "3127701": "Governador Valadares",
}

YEARS = list(range(2015, 2026))
EW_START = 1
EW_END = 53

API_URL = "https://info.dengue.mat.br/api/alertcity"


# =============================
# FUNÇÃO PARA COLETAR DADOS
# =============================

def fetch_city_data(ibge_code, year):
    params = {
        "geocode": ibge_code,
        "disease": "dengue",
        "format": "csv",
        "ew_start": EW_START,
        "ew_end": EW_END,
        "ey_start": year,
        "ey_end": year,
    }

    try:
        url = API_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        df = pd.read_csv(url)

        if df.empty:
            print(f"[AVISO] Sem dados para {ibge_code} em {year}")
            return None

        # Campo de data muda conforme a cidade; lidamos automaticamente
        date_col = "data" if "data" in df.columns else "data_iniSE"

        # converter timestamp se necessário
        if df[date_col].dtype != "object":
            df[date_col] = pd.to_datetime(df[date_col], unit="ms")
        else:
            df[date_col] = pd.to_datetime(df[date_col])

        df["year"] = df[date_col].dt.year
        df["month"] = df[date_col].dt.month

        # manter apenas casos observados (não estimados)
        df_monthly = (
            df.groupby(["year", "month"])["dengue_cases"]
            .sum()
            .reset_index()
        )
        df_monthly["municipality_code_ibge"] = ibge_code

        return df_monthly

    except Exception as e:
        print(f"[ERRO] {ibge_code}, ano {year}: {e}")
        return None


# =============================
# COLETAR PARA TODAS AS CIDADES
# =============================

all_data = []

for ibge, name in CITIES.items():
    print(f"\n📌 Coletando dados para: {ibge} - {name}")
    for year in YEARS:
        df = fetch_city_data(ibge, year)
        if df is not None:
            all_data.append(df)

# =============================
# UNIR E SALVAR
# =============================

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["municipality_code_ibge", "year", "month"])

    # salva o CSV final
    final_df.to_csv("./data/data_factory/dengue_monthly_2015_2025.csv", sep=";", index=False)

    print("\n🎉 Arquivo gerado com sucesso: dengue_monthly_2015_2025.csv")
else:
    print("Nenhum dado coletado.")
