#bibliotecas
import pandas as pd
import numpy as np
import re as re
import plotly.express as px
import folium
import haversine
import streamlit as st
from pathlib import Path
from haversine import haversine
from datetime import datetime
from streamlit_folium import folium_static

#dataset
file_path = Path("dataset/train.csv")

#ler arquivo CSV
df = pd.read_csv(file_path)

#faz uma cópia do df
dfcopy = df.copy()

#limpa todos os espaços em branco nas strings
dfcopy.loc[:,"ID"] = dfcopy.loc[:,"ID"].str.strip()
dfcopy.loc[:,"Delivery_person_ID"] = dfcopy.loc[:,"Delivery_person_ID"].str.strip()
dfcopy.loc[:,"Road_traffic_density"] = dfcopy.loc[:,"Road_traffic_density"].str.strip()
dfcopy.loc[:,"Type_of_order"] = dfcopy.loc[:,"Type_of_order"].str.strip()
dfcopy.loc[:,"Type_of_vehicle"] = dfcopy.loc[:,"Type_of_vehicle"].str.strip()
dfcopy.loc[:,"Festival"] = dfcopy.loc[:,"Festival"].str.strip()
dfcopy.loc[:,"City"] = dfcopy.loc[:,"City"].str.strip()

dfcopy["Weatherconditions"] = dfcopy["Weatherconditions"].str.replace("conditions ", "")
linhas = dfcopy["Weatherconditions"] != "NaN"
dfcopy = dfcopy.loc[linhas,:]

#excluindo linhas vazias do multiple_deliveries
linhas = dfcopy["multiple_deliveries"] != "NaN"
dfcopy = dfcopy.loc[linhas, :]

#excluindo linhas vazias do City
linhas = dfcopy["City"] != "NaN"
dfcopy = dfcopy.loc[linhas, :]

#excluindo linhas vazias do Road_traffic_density
linhas = dfcopy["Road_traffic_density"] != "NaN"
dfcopy = dfcopy.loc[linhas, :]

#excluindo linhas vazias no Delivery_person_Age
linhas = dfcopy["Delivery_person_Age"] != "NaN "
dfcopy = dfcopy.loc[linhas,:]

#conversão do tipo Delivery_person_Age para inteiro
#dfcopy["Delivery_person_Age"] = dfcopy["Delivery_person_Age"].astype(int)

#conversão do tipo Delivery_person_Ratings para float
dfcopy["Delivery_person_Ratings"] = dfcopy["Delivery_person_Ratings"].astype(float)

#conversão do tipo Time_taken(min) para string
dfcopy['Time_taken(min)'] = dfcopy['Time_taken(min)'].astype(str)
#conversão do tipo multiple_deliveries para string
#dfcopy["multiple_deliveries"] = dfcopy["multiple_deliveries"].astype(int)

#conversão do tipo Order_Date para data
dfcopy["Order_Date"] = pd.to_datetime(dfcopy["Order_Date"],format='%d-%m-%Y')

#trata a coluna Time_taken(min) para mostrar apenas números, mas ficou entre []
#dfcopy = dfcopy.reset_index(drop=True)
#for i in range(len(dfcopy)):
    #dfcopy.loc[i, 'Time_taken(min)'] = re.findall(r'\d+', dfcopy.loc[i, 'Time_taken(min)'])

#trata a coluna Time_taken(min) para mostrar apenas números, sem os []
dfcopy = dfcopy.reset_index(drop=True)
for i in range(len(dfcopy)):
    extracted_values = re.findall(r'\d+', dfcopy.loc[i, 'Time_taken(min)'])
    if extracted_values:
        dfcopy.loc[i, 'Time_taken(min)'] = extracted_values[0]

dfcopy["Time_taken(min)"] = dfcopy["Time_taken(min)"].astype(int)

# ====================================================================================
# LAYOUT NO STREAMLIT
# ====================================================================================

st.set_page_config(
    page_title="Cury Company Dashboard - Visão Entregadores",
    page_icon="🛵",  # Emoji de alvo
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================================================
# COMEÇA A BARRA LATERAL NO STREAMLIT
# ====================================================================================

# barra lateral

#date_slider = st.sidebar.slider(
#    "Indique o Intervalo",
#    value=datetime(2022,4,13),
#    min_value=datetime(2022,2,11),
#    max_value=datetime(2022,4,6),
#    format="DD-MM-YYYY")

#selecao = dfcopy["Order_Date"] < date_slider
#dfcopy = dfcopy.loc[selecao,:]

# ====================================================================================
# SLIDER DE DATA
# ====================================================================================

# Configurando o slider para selecionar um intervalo de datas
date_slider = st.sidebar.slider(
    "Selecione as datas",
    value=(datetime(2022,2,11), datetime(2022,4,6)),  # Tupla com data inicial e final
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    format="DD-MM-YYYY"
)

# Você pode acessar as datas selecionadas assim:
data_inicial, data_final = date_slider
#st.write("Data Inicial:", data_inicial)
#st.write("Data Final:", data_final)

# ====================================================================================
# FILTRO DA DATA
# ====================================================================================

# Agora você pode usar essas datas para filtrar o seu DataFrame
selecao = (dfcopy["Order_Date"] >= data_inicial) & (dfcopy["Order_Date"] <= data_final)
dfcopy = dfcopy.loc[selecao, :]

# ====================================================================================
# FILTRO DO TRÁFEGO
# ====================================================================================

city = st.sidebar.multiselect(
    "Selecione a cidade",
    ["Metropolitian","Urban","Semi-Urban"],
    default = ["Metropolitian","Urban","Semi-Urban"])

selecao = dfcopy["City"].isin(city)
dfcopy = dfcopy.loc[selecao, :]

traffic = st.sidebar.multiselect(
    "Selecione as condições de trânsito",
    ["Low","Medium","High","Jam"],
    default = ["Low","Medium","High","Jam"])

selecao = dfcopy["Road_traffic_density"].isin(traffic)
dfcopy = dfcopy.loc[selecao, :]

weather = st.sidebar.multiselect(
    "Selecione o clima",
    ["Cloudy","Fog","Sandstorms","Stormy","Sunny","Windy"],
    default = ["Cloudy","Fog","Sandstorms","Stormy","Sunny","Windy"])

selecao = dfcopy["Weatherconditions"].isin(weather)
dfcopy = dfcopy.loc[selecao, :]


#st.dataframe(dfcopy)

# ====================================================================================
# TERMINA A BARRA LATERAL
# ====================================================================================

# header
st.title("Cury Company Dashboard")
st.header(":motor_scooter: _Visão Entregadores_")

# ====================================================================================
# ABAS
# ====================================================================================

# abas
tab1, tab2 = st.tabs(["Desempenho","Aproveitamento"])

# Desempenho
with tab1:
    #Cria Quatro Colunas
    col1,col2,col3,col4 = st.columns(4,gap="small")
    
    with col1:
        maior = dfcopy.loc[:,"Delivery_person_Age"].max()
        col1.metric("Maior Idade",maior)
        
    with col2:
        menor = dfcopy.loc[:,"Delivery_person_Age"].min()
        col2.metric("Menor Idade",menor)
    
    with col3:
        melhor = dfcopy.loc[:,"Vehicle_condition"].max()
        col3.metric("Melhor Condição de Veículo",melhor)

    with col4:
        pior = dfcopy.loc[:,"Vehicle_condition"].min()
        col4.metric("Pior Condição de Veículo",pior)

# =========== Linha Horizontal ============
    st.divider()
# =========== Linha Horizontal ============
      
    # Na mesma tab - Cria Duas Colunas
    col1,col2 = st.columns([0.40,0.60],gap="small")
    
    with col1:
        
        st.markdown("**Avaliação Média por Entregador**")
        media = dfcopy.loc[:,["Delivery_person_ID","Delivery_person_Ratings"]].groupby("Delivery_person_ID").mean().reset_index()
        st.dataframe(media,height=493)
    
    with col2:
        
        st.markdown("**Avaliação Média e Desvio Padrão por Trânsito**")
        # Usando 'agg' para calcular a média ('mean') e o desvio padrão ('std') juntos
        trafego = dfcopy.loc[:,["Delivery_person_Ratings", "Road_traffic_density"]].groupby("Road_traffic_density").agg({"Delivery_person_Ratings": ['mean', 'std']}).reset_index()
        trafego.columns = ["Road_traffic_density","Delivery_person_Ratings_mean","Delivery_person_Ratings_std"]
        st.dataframe(trafego)
        
        st.markdown("**Avaliação Média e Desvio Padrão por Clima**")
        clima = dfcopy.loc[:,["Delivery_person_Ratings","Weatherconditions"]].groupby("Weatherconditions").agg(['mean','std']).reset_index()
        clima.columns = ["Weatherconditions","Delivery_person_Ratings_mean","Delivery_person_Ratings_std"]
        st.dataframe(clima)

# Aproveitamento
with tab2:
    
    col1,col2 = st.columns(2,gap="small")
    
    with col1:
        st.markdown("**Entregadores Mais Rápidos**")
        dfcopy2 = dfcopy.loc[:,["Delivery_person_ID","City","Time_taken(min)"]].groupby(["City","Delivery_person_ID"]).mean().sort_values(["City","Time_taken(min)"], ascending=True).reset_index()

        dfcopy_aux1 = dfcopy2.loc[dfcopy2["City"] == "Metropolitian",:].head(10)
        dfcopy_aux2 = dfcopy2.loc[dfcopy2["City"] == "Urban",:].head(10)
        dfcopy_aux3 = dfcopy2.loc[dfcopy2["City"] == "Semi-Urban",:].head(10)

        dfcopy3 = pd.concat([dfcopy_aux1,dfcopy_aux2,dfcopy_aux3]).reset_index(drop=True)
        st.dataframe(dfcopy3,height=400)
    
    with col2:
        st.markdown("**Entregadores Mais Lentos**")
        dfcopy2 = dfcopy.loc[:,["Delivery_person_ID","City","Time_taken(min)"]].groupby(["City","Delivery_person_ID"]).mean().sort_values(["City","Time_taken(min)"], ascending=False).reset_index()

        dfcopy_aux1 = dfcopy2.loc[dfcopy2["City"] == "Metropolitian",:].head(10)
        dfcopy_aux2 = dfcopy2.loc[dfcopy2["City"] == "Urban",:].head(10)
        dfcopy_aux3 = dfcopy2.loc[dfcopy2["City"] == "Semi-Urban",:].head(10)

        dfcopy3 = pd.concat([dfcopy_aux1,dfcopy_aux2,dfcopy_aux3]).reset_index(drop=True)
        st.dataframe(dfcopy3,height=400)