# Arboviral Epidemic Predictor
Artificial intelligence-based data organization and modeling for arboviral epidemic prediction.

<hr>

# Instalando Dependências

Apenas executar o comando no terminal:

```bash
pip install -r requirements.txt
``` 
# Exibindo o Dashboard

Apenas executar o comando no terminal:

```bash
streamlit run src/dashboard.py
``` 

Ou executar pelo windows:
```bash
python -m streamlit run src\dashboard.py
```

# Campos da tabela

| **Name**                   | **Description**                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------- |
| **id**                     | Unique identifier for each row; primary key of the dataset.                                        |
| **year**                   | Year of the observation (2000–2025).                                                               |
| **month**                  | Month of the observation (1–12).                                                                   |
| **municipality_code_ibge** | Official 7-digit IBGE municipality code (Brazil).                                                  |
| **municipality_name**      | Name of the municipality corresponding to the IBGE code. May be stored in a separate lookup table. |
| **dengue_cases**           | Number of reported dengue cases in the month.                                                      |
| **estimated_population**   | Estimated population of the municipality (e.g., IBGE 2022).                                        |
| **rainfall_mm**            | Total monthly precipitation (millimeters).                                                         |
| **average_humidity**       | Average monthly relative humidity (%).                                                             |
| **average_temperature**    | Average monthly temperature (°C).                                                                  |

<hr>

# Prefixo código de municípios IBGE
| UF | Código | Estado              |
| -- | ------ | ------------------- |
| 11 | RO     | Rondônia            |
| 12 | AC     | Acre                |
| 13 | AM     | Amazonas            |
| 14 | RR     | Roraima             |
| 15 | PA     | Pará                |
| 16 | AP     | Amapá               |
| 17 | TO     | Tocantins           |
| 21 | MA     | Maranhão            |
| 22 | PI     | Piauí               |
| 23 | CE     | Ceará               |
| 24 | RN     | Rio Grande do Norte |
| 25 | PB     | Paraíba             |
| 26 | PE     | Pernambuco          |
| 27 | AL     | Alagoas             |
| 28 | SE     | Sergipe             |
| 29 | BA     | Bahia               |
| 31 | MG     | Minas Gerais        |
| 32 | ES     | Espírito Santo      |
| 33 | RJ     | Rio de Janeiro      |
| 35 | SP     | São Paulo           |
| 41 | PR     | Paraná              |
| 42 | SC     | Santa Catarina      |
| 43 | RS     | Rio Grande do Sul   |
| 50 | MS     | Mato Grosso do Sul  |
| 51 | MT     | Mato Grosso         |
| 52 | GO     | Goiás               |
| 53 | DF     | Distrito Federal    |
