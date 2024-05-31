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
    page_title="Cury Company Dashboard - Visão Empresa",
    page_icon="🎯",  # Emoji de alvo
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
st.header(":dart: _Visão Empresa_")

# ====================================================================================
# ABAS
# ====================================================================================

# abas
tab1, tab2, tab3 = st.tabs(["Visão Gerencial","Visão Tática","Visão Geográfica"])

# ====================================================================================
# CONTEÚDO DAS ABAS
# ====================================================================================

# Visão Gerencial
with tab1:
    #Quantidade de Pedidos por Dia
    st.markdown("**Quantidade de Pedidos por Dia**")
    cols = ["ID","Order_Date"]
    dfcopy_aux = dfcopy.loc[:,cols].groupby("Order_Date").count().reset_index()
    dfcopy_aux.head()
    
    #desenhar o gráfico de linhas
    fig = px.bar(dfcopy_aux,x="Order_Date",y="ID",color_discrete_sequence=["#184A7D"])
    st.plotly_chart(fig,user_container_width=True)

    #Cria Duas Colunas
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("**Pedidos por Tipo de Tráfego**")
        #agrupar pedidos por tipo de tráfego // não esquecer de resetar o index
        dfcopy_aux = dfcopy.loc[:,["ID","Road_traffic_density"]].groupby("Road_traffic_density").count().reset_index()
        dfcopy_aux.head()
        #faz um gráfico de pizza
        fig = px.pie(dfcopy_aux, values="ID", names="Road_traffic_density",color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig,user_container_width=True)
    
    with col2:
        st.markdown("**Volume de Pedidos por Cidade e Tráfego**")
        #Eu preciso contar o número de pedidos, agrupados por cidade e tipo de veículo e desenhar um gráfico de bolha.
        dfcopy_aux = dfcopy.loc[:,["ID","City","Road_traffic_density"]].groupby(["City","Road_traffic_density"]).count().reset_index()
        #grfáfico bolha é gráfico de dispersão // scatter plot
        fig = px.scatter(dfcopy_aux,x="City",y="Road_traffic_density",size="ID",color="City",color_discrete_sequence=px.colors.qualitative.Bold)           
        st.plotly_chart(fig,user_container_width=True)

#Visão Tática
with tab2:
    st.markdown("**Quantidade de Pedidos por Semana**")
    #cria a nova coluna semana do ano
    dfcopy["Week_of_Year"] = dfcopy["Order_Date"].dt.strftime("%U")
    #contar ID agruprando por semana
    cols = ["ID","Week_of_Year"]
    dfcopy_aux = dfcopy.loc[:,cols].groupby("Week_of_Year").count().reset_index()
    dfcopy_aux.head()
    #faz o gráfico de linhas
    fig = px.line(dfcopy_aux,x="Week_of_Year",y="ID",color_discrete_sequence=["#D31D6C"])
    st.plotly_chart(fig,user_container_width=True)

    st.markdown("**Participação Percentual dos Entregadores nos Pedidos Semanais**")
    #Calcula do número de entregas por semana e o cálculo do número de entregadores únicos por semana e vou dividir os dois valores, exibindo-os em um gráfico de linha.
    #conta quantas entregas foram feitas a cada semana
    dfcopy_aux1 = dfcopy.loc[:,["ID","Week_of_Year"]].groupby("Week_of_Year").count().reset_index()

    #conta quantas entregas cada um fez por semana // não dá para fazer o count pq esse ID parace várias vezes
    #então usamos o nunique que conta quantas vezes parace cada um deles
    dfcopy_aux2 = dfcopy.loc[:,["Delivery_person_ID","Week_of_Year"]].groupby("Week_of_Year").nunique().reset_index()

    #juntar as duas novas tabelas
    dfcopy_aux = pd.merge(dfcopy_aux1,dfcopy_aux2,how="inner")

    #agora vou criar a nova coluna que mostra o calculo, razao da entre de cada entregador por entregas semanais
    #calcula a proporção de pedidos atribuída a cada entregador
    dfcopy_aux["Order_by_Delivery_Person"] = dfcopy_aux["ID"] / dfcopy_aux["Delivery_person_ID"]

    #desenha o gráfico
    fig = px.line(dfcopy_aux,x="Week_of_Year",y="Order_by_Delivery_Person",color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig,user_container_width=True)

#Visão Geográfica
with tab3:
    st.markdown("**Localização dos Restaurantes**")
    # Seu DataFrame agrupado
    df_agrupado = dfcopy.loc[:,["City","Delivery_location_latitude","Delivery_location_longitude","Road_traffic_density"]].groupby(["City","Road_traffic_density"]).median().reset_index()

    # Inicializando o mapa na localização central dos dados
    mapa = folium.Map(location=[df_agrupado["Delivery_location_latitude"].median(), df_agrupado["Delivery_location_longitude"].median()], zoom_start=7)

    # Adicionando os pinos ao mapa
    for _, row in df_agrupado.iterrows():
        folium.Marker(
            location=[row["Delivery_location_latitude"], row["Delivery_location_longitude"]],
            popup=f"Cidade: {row['City']}\nDensidade do Tráfego: {row['Road_traffic_density']}",
            tooltip=row["City"]
            ).add_to(mapa)
    # Exibindo o mapa
    folium_static(mapa,width=980,height=500)


#print(dfcopy.head())

