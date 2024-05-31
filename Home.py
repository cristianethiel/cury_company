import streamlit as st

st.set_page_config(
    page_title="Cury Company Dashboard",
    page_icon="🫕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ====================================================================================
# BARRA LATERAL
# ====================================================================================
st.title(":fondue: Cury Company Dashboard")
st.header("Selecione a Visão")

st.page_link("pages/1_Visao_Empresa.py", label=" Visão Empresa", icon="🎯")
st.page_link("pages/2_Visao_Entregadores.py", label="Visão Entregadores", icon="🛵")
st.page_link("pages/3_Visao_Restaurantes.py", label="Visão Restaurantes", icon="🛎️")


# ====================================================================================
# TERMINA A BARRA LATERAL
# ====================================================================================
