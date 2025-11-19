import pandas as pd

# Carregar tabelas
master = pd.read_csv("./data/data_factory/master_table_corrigida.csv", sep=";")
dengue = pd.read_csv("./data/data_factory/dengue_monthly_2015_2025.csv", sep=";")

# Remover coluna dengue_cases da master (ela é lixo aqui)
if "dengue_cases" in master.columns:
    master = master.drop(columns=["dengue_cases"])

# Renomear "casos" -> "dengue_cases"
dengue = dengue.rename(columns={"casos": "dengue_cases"})

# Garantir tipos iguais para merge
master["municipality_code_ibge"] = master["municipality_code_ibge"].astype(int)
dengue["municipality_code_ibge"] = dengue["municipality_code_ibge"].astype(int)

# Merge correto
merged = master.merge(
    dengue,
    on=["municipality_code_ibge", "year", "month"],
    how="left"
)

# Preencher nulos
merged["dengue_cases"] = merged["dengue_cases"].fillna(0).astype(int)

# Salvar resultado
merged.to_csv("./data/data_factory/final_table.csv", sep=";", index=False)

print("Tabela final gerada com sucesso!")
