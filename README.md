# Arboviral Epidemic Predictor
Artificial intelligence-based data organization and modeling for arboviral epidemic prediction.

<hr>

# Campos CSV
| **Nome Melhorado**    | **Observações / Significado**                                                         |
| --------------------- | ------------------------------------------------------------------------------------- |
| id_registro           | Identificador único da linha; chave primária da tabela.                               |
| ano                   | Ano da observação (2000–2025).                                                        |
| mes                   | Mês da observação (1–12).                                                             |
| codigo_municipio_ibge | Código IBGE oficial do município (7 dígitos).                                         |
| nome_municipio        | Nome do município correspondente ao código IBGE. Pode ser mantido em tabela auxiliar. |
| casos_dengue          | Total de casos notificados de dengue no mês.                                          |
| casos_chikungunya     | Total de casos notificados de chikungunya no mês.                                     |
| casos_zika            | Total de casos notificados de zika no mês.                                            |
| casos_totais          | Soma dengue + chikungunya + zika (campo opcional, mas útil).                          |
| populacao_estimada    | População estimada do município (ex.: base 2022 do IBGE).                             |
| chuva_mm              | Total de precipitação mensal (mm).                                                    |
| umidade_media         | Média mensal de umidade relativa do ar (%).                                           |
| temperatura_media     | Média mensal de temperatura (°C).                                                     |
| indice_breve          | Índice de Breteau (criadouros positivos para Aedes por 100 imóveis).                  |
| indice_predial        | Índice Predial (percentual de imóveis com larvas do Aedes).                           |
| indice_recipient      | Índice de Recipientes (percentual de recipientes com larvas).                         |

<hr>

# Prefixo do Código de Município IBGE
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