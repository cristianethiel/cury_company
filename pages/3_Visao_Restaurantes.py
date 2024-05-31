#bibliotecas
import pandas as pd
import numpy as np
import re as re
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="Cury Company Dashboard - Visão Restaurantes",
    page_icon="🛎️",  # Emoji de alvo
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================================================
# COMEÇA A BARRA LATERAL NO STREAMLIT
# ====================================================================================

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
st.header(":bellhop_bell: _Visão Restaurantes_")

# ====================================================================================
# ABAS
# ====================================================================================

# abas
tab1, tab2 = st.tabs(["Visão Gerencial","Tempo de Entrega"])

with tab1:
   with st.container(): #linha1 
        col1,col2,col3,col4,col5,col6 = st.columns(6,gap="small")
                
        with col1:
            entregadores_unicos = dfcopy["Delivery_person_ID"].unique().shape[0]
            col1.metric("Entregadores Únicos", entregadores_unicos)

        with col2:
            cols = ["Restaurant_latitude","Restaurant_longitude","Delivery_location_latitude","Delivery_location_longitude"]
            dfcopy["Distancy"] = dfcopy.loc[:,cols].apply(lambda x: haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),(x["Delivery_location_latitude"],x["Delivery_location_longitude"])), axis=1)
            #numpy round para ser apenas 2 números após a vírgula
            distancia_media = np.round(dfcopy["Distancy"].mean(),2)
            dfcopy["Distancy"] = dfcopy["Distancy"].astype(float)
            print(f"A distância média é de {distancia_media}.")
            col2.metric("Distância Média",distancia_media)

        with col3:
            tempo_medio = np.round(dfcopy.loc[dfcopy["Festival"] == "Yes","Time_taken(min)"].mean(),2)
            col3.metric("Tempo Médio (Festival)",tempo_medio)
        
        with col4:
            desvio_padrao = np.round(dfcopy.loc[dfcopy["Festival"] == "Yes","Time_taken(min)"].std(),2)
            col4.metric("Desvio Padrão (Festival)",desvio_padrao)

        with col5:
            tempo_medio = np.round(dfcopy.loc[dfcopy["Festival"] == "No","Time_taken(min)"].mean(),2)
            col5.metric("Tempo Médio",tempo_medio)

        with col6:
            desvio_padrao = np.round(dfcopy.loc[dfcopy["Festival"] == "No","Time_taken(min)"].std(),2)
            col6.metric("Desvio Padrão",desvio_padrao)

        st.divider()

        col1,col2 = st.columns([0.40,0.60],gap="small")
                    
        with col1:
            st.markdown("**Tempo de Entrega por Cidade**")
            dfcopy_aux = dfcopy.loc[:, ["City","Time_taken(min)"]].groupby("City").agg({"Time_taken(min)":["mean","std"]})

            dfcopy_aux.columns = ["Tempo Médio","Desvio Padrão"]
            dfcopy_aux["Tempo Médio"] = dfcopy_aux["Tempo Médio"].apply(lambda x: f"{x:.2f}")
            dfcopy_aux["Desvio Padrão"] = dfcopy_aux["Desvio Padrão"].apply(lambda x: f"{x:.2f}")

            dfcopy_aux = dfcopy_aux.reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(name="Control",x=dfcopy_aux["City"],y=dfcopy_aux["Tempo Médio"],error_y=dict(type="data", array=dfcopy_aux["Desvio Padrão"])))
            fig.update_layout(barmode="group")
            
            st.plotly_chart(fig)
        
        with col2:
            st.markdown("**Distância Média por Cidade**")
            cols = ["Restaurant_latitude","Restaurant_longitude","Delivery_location_latitude","Delivery_location_longitude"]
            dfcopy["Distancy"] = dfcopy.loc[:,cols].apply(lambda x: haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),(x["Delivery_location_latitude"],x["Delivery_location_longitude"])), axis=1)

            distancia_media_cidade = dfcopy.loc[:,["City","Distancy"]].groupby("City").mean().reset_index()
            dfcopy["Distancy"] = dfcopy["Distancy"].astype(float)
            #apenas duas casas decimais
            distancia_media_cidade["Distancy"] = distancia_media_cidade["Distancy"].apply(lambda x: f"{x:.2f}")
            #faz um gráfico de pizza
            #fig = px.pie(distancia_media_cidade, values="Distancy", names="City", color_discrete_sequence=px.colors.qualitative.Prism)
            #cores
            color_sequence = ['#5F4690', '#11A579', '#38A6A5', '#38A6A5']

            fig = go.Figure(data=[go.Pie(labels=distancia_media_cidade["City"],values=distancia_media_cidade["Distancy"],marker=dict(colors=color_sequence),textinfo="value",hoverinfo="label",pull=[0,0.1,0])])
            st.plotly_chart(fig,user_container_width=True)

with tab2:
    col1,col2 = st.columns([0.40,0.60],gap="large")
    with col1:
        st.markdown("**Tempo de Entrega por Condição de Trânsito**")
        dfcopy_aux = dfcopy.loc[:,["City","Road_traffic_density","Time_taken(min)"]].groupby(["City","Road_traffic_density"]).agg({"Time_taken(min)":["mean","std"]})        
        dfcopy_aux.columns = ["Tempo Médio","Desvio Padrão"]
        dfcopy_aux = dfcopy_aux.reset_index()

        fig = px.sunburst(dfcopy_aux,path=["City","Road_traffic_density"],values="Tempo Médio",color="Desvio Padrão",color_continuous_scale="Magma",color_continuous_midpoint=np.average(dfcopy_aux["Desvio Padrão"]))
        st.plotly_chart(fig)

    with col2:
        st.markdown("**Tempo de Entrega por Cidade e Tipo de Pedido**")
        dfcopy_aux = dfcopy.loc[:,["City","Type_of_order","Time_taken(min)"]].groupby(["City","Type_of_order"]).agg({"Time_taken(min)":["mean","std"]}).reset_index()
        dfcopy_aux.columns = ["City","Type_of_order","Time_taken(min)_mean","Time_taken(min)_std"]
        st.dataframe(dfcopy_aux,height=400)