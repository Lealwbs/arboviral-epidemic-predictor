import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

#path para importar os módulos existentes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alerts import Alert
from predictor import Predictor 

st.set_page_config(
    page_title="Arboviral Predictor - Dashboard",
    page_icon="🦟",
    layout="wide"
)

#caminho do arquivo de forma global para usar no load_data e no Predictor
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'master_table.csv')

# ETL Simples para o Front
@st.cache_data
def load_data():
    try:
        # O delimitador detectado no arquivo enviado é ';'
        df = pd.read_csv(DATA_PATH, sep=';') 
        return df
    except FileNotFoundError:
        st.error(f"Arquivo master_table.csv não encontrado em: {DATA_PATH}")
        return pd.DataFrame()

df = load_data()

# sidebar: Filtros de Recuperação da Informação 
st.sidebar.header("⚙️ Filtros de Recuperação")

# Filtro de Cidade
if not df.empty:
    cidades = df['municipality_name'].unique()
    cidade_selecionada = st.sidebar.selectbox("Selecione o Município:", cidades)

    # Filtrar DF pela cidade
    df_city = df[df['municipality_name'] == cidade_selecionada].copy()

    # Filtro de Ano
    anos = sorted(df_city['year'].unique())
    # Seleciona o último ano disponível por padrão
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano de Referência:", anos, index=len(anos)-1)

    # Filtro de Dados (Filtro lógico AND implícito)
    df_filtered = df_city[df_city['year'] == ano_selecionado]
else:
    st.warning("Base de dados vazia ou não carregada.")
    st.stop()

# interface principal

st.title(f"🦟 Monitoramento Arboviral: {cidade_selecionada}")
st.markdown("### Plataforma de Apoio à Decisão para Gestores de Saúde")

# KPIs (Indicadores Chave)
col1, col2, col3, col4 = st.columns(4)
total_casos = df_filtered['dengue_cases'].sum()
media_temp = df_filtered['average_temperature'].mean()
total_chuva = df_filtered['rainfall_mm'].sum()
populacao = df_filtered['estimated_population'].iloc[0] if not df_filtered.empty else 0

col1.metric("Total de Casos (Ano)", f"{total_casos}")
col2.metric("Temp. Média", f"{media_temp:.1f} °C")
col3.metric("Precipitação Acumulada", f"{total_chuva:.1f} mm")
col4.metric("População Estimada", f"{populacao:,.0f}")

# Séries Temporais

st.subheader(f"📉 Evolução Epidemiológica e Climática - {ano_selecionado}")

# Gráfico Misto: Barras (Chuva) e Linha (Casos)
fig = px.bar(
    df_filtered, 
    x='month', 
    y='rainfall_mm', 
    title='Casos de Dengue vs Precipitação',
    labels={'rainfall_mm': 'Chuva (mm)', 'month': 'Mês', 'dengue_cases': 'Casos'},
    color_discrete_sequence=['lightblue'],
    opacity=0.6
)

# Adicionar linha de casos
fig.add_scatter(
    x=df_filtered['month'], 
    y=df_filtered['dengue_cases'], 
    mode='lines+markers', 
    name='Casos de Dengue',
    yaxis='y2',
    line=dict(color='red', width=3)
)

# Ajustar layout para eixo duplo
fig.update_layout(
    yaxis2=dict(
        title='Número de Casos',
        overlaying='y',
        side='right'
    ),
    xaxis=dict(tickmode='linear', tick0=1, dtick=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Alerta e Tratamento Descritivo (XML/CAP) 
st.markdown("---")
st.subheader("📢 Geração de Alerta (Padrão CAP v1.2)")

col_pred, col_xml = st.columns([1, 2])

# código IBGE da cidade selecionada (como string, necessário para o Predictor)
codigo_ibge = str(df_filtered['municipality_code_ibge'].iloc[0])

# Preparar datas para previsão (Próximo Mês Real)
# Nota: O predictor.py lança erro se tentarmos prever datas passadas. 
# Por isso, calculamos aqui o próximo mês em relação a "hoje" para acionar a IA.
data_atual = datetime.now()
ano_prev = data_atual.year
mes_prev = data_atual.month + 1
if mes_prev > 12:
    mes_prev = 1
    ano_prev += 1

# Variável para armazenar o objeto de alerta gerado
alerta_gerado = None

with col_pred:
    st.info(f"Previsão via IA (Random Forest)")
    st.caption(f"Simulando previsão para: **{mes_prev:02d}/{ano_prev}**")
    
    try:
        
        # integrando com o predictor.py
        with st.spinner("Executando modelo preditivo..."):
            # Instancia o Predictor com o caminho do CSV
            modelo = Predictor(tablepath=DATA_PATH)
            
            # Chama o método predict_outbreak
            # Isso treina o modelo em tempo real e retorna o objeto Alert preenchido
            alerta_gerado = modelo.predict_outbreak(
                city_code=codigo_ibge, 
                year=str(ano_prev), 
                month=str(mes_prev)
            )

        # Definir cor baseada na severidade retornada pelo modelo
        cor_risco = "green"
        if alerta_gerado.severity == "Moderate":
            cor_risco = "orange"
        elif alerta_gerado.severity == "Severe":
            cor_risco = "red"

        # Tradução visual para o Dashboard
        traducao_risco = {
            "Minor": "Baixo (Monitoramento)",
            "Moderate": "Médio (Alerta)",
            "Severe": "Alto Risco (Crítico)"
        }
        
        texto_risco = traducao_risco.get(alerta_gerado.severity, "Desconhecido")

        st.markdown(f"**Risco Calculado:**")
        st.markdown(f"<h2 style='color:{cor_risco};'>{texto_risco}</h2>", unsafe_allow_html=True)
        
        st.metric("Casos Previstos", f"{alerta_gerado.predicted_cases}")
        st.markdown(f"**Acurácia do Modelo:** {alerta_gerado.certainly}")

    except ValueError as e:
        # Captura erros do predictor (ex: cidade não mapeada ou data inválida)
        st.error(f"Erro na Predição: {e}")
        st.warning("Verifique se a cidade selecionada está no dicionário IBGE_CITY_CODES do predictor.py")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")

mes_prev += 1
if mes_prev > 12:
    mes_prev = 1
    ano_prev += 1

with col_pred:
    st.info(f"Previsão via IA (Random Forest)")
    st.caption(f"Simulando previsão para: **{mes_prev:02d}/{ano_prev}**")
    
    try:
        
        # integrando com o predictor.py
        with st.spinner("Executando modelo preditivo..."):
            # Instancia o Predictor com o caminho do CSV
            modelo = Predictor(tablepath=DATA_PATH)
            
            # Chama o método predict_outbreak
            # Isso treina o modelo em tempo real e retorna o objeto Alert preenchido
            alerta_gerado = modelo.predict_outbreak(
                city_code=codigo_ibge, 
                year=str(ano_prev), 
                month=str(mes_prev)
            )

        # Definir cor baseada na severidade retornada pelo modelo
        cor_risco = "green"
        if alerta_gerado.severity == "Moderate":
            cor_risco = "orange"
        elif alerta_gerado.severity == "Severe":
            cor_risco = "red"

        # Tradução visual para o Dashboard
        traducao_risco = {
            "Minor": "Baixo (Monitoramento)",
            "Moderate": "Médio (Alerta)",
            "Severe": "Alto Risco (Crítico)"
        }
        
        texto_risco = traducao_risco.get(alerta_gerado.severity, "Desconhecido")

        st.markdown(f"**Risco Calculado:**")
        st.markdown(f"<h2 style='color:{cor_risco};'>{texto_risco}</h2>", unsafe_allow_html=True)
        
        st.metric("Casos Previstos", f"{alerta_gerado.predicted_cases}")
        st.markdown(f"**Acurácia do Modelo:** {alerta_gerado.certainly}")

    except ValueError as e:
        # Captura erros do predictor (ex: cidade não mapeada ou data inválida)
        st.error(f"Erro na Predição: {e}")
        st.warning("Verifique se a cidade selecionada está no dicionário IBGE_CITY_CODES do predictor.py")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")

with col_xml:
    st.write(" **Metadados do Alerta (Formato XML para Interoperabilidade):**")
    
    if alerta_gerado:
        # Exibe o XML gerado diretamente pelo método get_metadata da classe Alert
        # vindo de dentro do predictor.py
        st.code(alerta_gerado.get_metadata(), language='xml')
    else:
        st.warning("Aguardando geração da previsão para exibir o XML.")

#Gestão Arquivística
st.markdown("---")
with st.expander("🗄️ Metadados de Gestão Arquivística (Ciclo de Vida)"):
    if alerta_gerado:
        st.write(f"**Identificador Único:** {alerta_gerado.identifier}")
        st.write(f"**Data de Criação:** {alerta_gerado.sent}")
        st.write(f"**Fase Atual:** Corrente")
        
        if alerta_gerado.severity in ["Moderate", "Severe"]:
            st.warning("⚠️ Destinação Final Prevista: **Guarda Permanente** (Risco Alto/Médio)")
        else:
            st.info("♻️ Destinação Final Prevista: **Eliminação após 1 ano** (Risco Baixo)")
    else:
        st.write("Nenhum alerta gerado para análise arquivística.")