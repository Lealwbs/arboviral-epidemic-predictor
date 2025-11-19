import csv

CIDADES = {}

with open("./data/data_factory/municipios_mg.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        codigo = row["codigo_ibge"]
        CIDADES[codigo] = {
            "nome": row["nome"],
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"])
        }
