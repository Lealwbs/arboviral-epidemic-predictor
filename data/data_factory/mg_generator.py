import csv

# Lista das cidades desejadas
cidades_desejadas = {
    "Belo Horizonte",
    "Uberlândia",
    "Contagem",
    "Juiz de Fora",
    "Montes Claros",
    "Uberaba",
    "Ribeirão das Neves",
    "Governador Valadares",
    
}

# Normalização
cidades_desejadas_normalizadas = {c.lower().strip() for c in cidades_desejadas}

# Arquivos
entrada = "./data/data_factory/municipios.csv"
saida = "./data/data_factory/municipios_mg.csv"

with open(entrada, encoding="utf-8") as f_in:
    reader = csv.DictReader(f_in)

    fieldnames = reader.fieldnames  # preserva as mesmas colunas

    with open(saida, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            nome = row["nome"].lower().strip()
            codigo_uf = row["codigo_uf"].strip()

            # MG = código_uf 31
            if codigo_uf == "31" and nome in cidades_desejadas_normalizadas:
                writer.writerow(row)

print("municipios_mg.csv gerado com sucesso!")
