import pandas as pd
import openmeteo_requests
from openmeteo_requests.Client import OpenMeteoRequestsError
import requests_cache
import requests
import time
from retry_requests import retry
from load_cities import CIDADES as C
from datetime import datetime

CIDADES = C

# --- 2. Função para pegar População do IBGE (SIDRA) ---
def get_populacao_ibge(city_code):
    """
    Busca a estimativa populacional na Tabela 6579 do SIDRA (IBGE).
    Retorna um dicionário: {2015: 2500000, 2016: 2510000, ...}
    """
    print(f"   -> Buscando população no IBGE para {city_code}...")
    
    # Tabela 6579: Estimativas de População enviadas ao TCU
    # Variável 9324: População residente estimada
    url = f"https://apisidra.ibge.gov.br/values/t/6579/n6/{city_code}/v/9324/p/all"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        pop_dict = {}
        for item in data:
            # O SIDRA retorna um json onde 'D2C' é o ano e 'V' é o valor
            try:
                ano = int(item['D2C']) # Coluna do Ano/Período
                valor = int(item['V']) # Valor da População
                pop_dict[ano] = valor
            except (ValueError, KeyError):
                continue
                
        # TRUQUE PARA O CENSO 2022 e anos recentes não cobertos pela tab 6579
        # Se faltar 2023/2024, repetimos o último valor conhecido (estratégia de fallback)
        anos_necessarios = range(2015, 2026)
        ultimo_valido = list(pop_dict.values())[-1] if pop_dict else 0
        
        for ano in anos_necessarios:
            if ano not in pop_dict:
                pop_dict[ano] = ultimo_valido
                
        return pop_dict
        
    except Exception as e:
        print(f"Erro ao buscar IBGE: {e}")
        return {}

# --- 3. Configuração da API Open-Meteo (Clima) ---
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

lista_dados = []

print("=== Iniciando Coleta de Dados (Clima + População) ===")

for cod_ibge, info in CIDADES.items():
    print(f"Processando {info['nome']}...")
    
    # 1. Busca a População Anual deste município
    populacao_anual = get_populacao_ibge(cod_ibge)
    
    # 2. Busca o Clima Histórico
    url = "https://archive-api.open-meteo.com/v1/archive"
    

# No loop das cidades:
    today_str = datetime.today().strftime('%Y-%m-%d') # Pega a data de hoje (ex: 2025-11-19)

    params = {
        "latitude": info['lat'],
        "longitude": info['lon'],
        "start_date": "2015-01-01",
        "end_date": today_str, # <--- Agora vai até o dia atual
        "daily": ["temperature_2m_mean", "precipitation_sum", "relative_humidity_2m_mean"],
        "timezone": "America/Sao_Paulo"
    }
    
    while True:
        try:
            responses = openmeteo.weather_api(url, params=params)
            break  # Sucesso → sai do loop
        except OpenMeteoRequestsError as e:
            msg = str(e)
            print("\n⚠️  Limite da API atingido. Aguardando 110 segundos...\n")
            print(f"Detalhes: {msg}")
            time.sleep(110)
            print("↻ Tentando novamente...\n")
            
    response = responses[0]
    
    # Processar dados diários do clima
    daily = response.Daily()
    dates = pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )
    
    df_daily = pd.DataFrame({
        "date": dates,
        "temp": daily.Variables(0).ValuesAsNumpy(),
        "rain": daily.Variables(1).ValuesAsNumpy(),
        "humidity": daily.Variables(2).ValuesAsNumpy()
    })
    
    # Agrupar por mês
    df_monthly = df_daily.resample('ME', on='date').agg({
        'temp': 'mean',
        'humidity': 'mean',
        'rain': 'sum'
    }).reset_index()
    
    # 3. Montagem Final da Tabela
    for _, row in df_monthly.iterrows():
        ano_atual = row['date'].year
        
        # Pega a população correta para aquele ano
        # Se não tiver o ano exato, usa 0 ou o fallback da função
        pop_do_ano = populacao_anual.get(ano_atual, 0)

        lista_dados.append({
            "municipality_code_ibge": cod_ibge,
            "municipality_name": info['nome'],
            "year": ano_atual,
            "month": row['date'].month,
            "dengue_cases": 0, # AINDA PRECISA PREENCHER DEPOIS
            "estimated_population": pop_do_ano, # <--- PREENCHIDO AUTOMATICAMENTE
            "rainfall_mm": round(row['rain'], 1),
            "average_temperature": round(row['temp'], 1),
            "average_humidity": round(row['humidity'], 1)
        })

# --- 4. Salvar ---
df_master = pd.DataFrame(lista_dados)
# Remove linhas futuras (caso a API traga o mês atual incompleto)
df_master = df_master[df_master['year'] <= 2025]

df_master.to_csv("./data/data_factory/master_table_corrigida.csv", sep=";", index=False)
print("\nSucesso! Arquivo 'master_table_corrigida.csv' gerado.")
print("Agora falta apenas preencher a coluna 'dengue_cases' com dados do InfoDengue/DATASUS.")