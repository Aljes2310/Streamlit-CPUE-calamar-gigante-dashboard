import pandas as pd
import plotly.express as px
import streamlit as st
import leafmap.foliumap as leafmap
import folium
from folium.plugins import Fullscreen, MousePosition

st.set_page_config(page_title="Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")

df = pd.read_csv("dfpota_3.csv", encoding='latin-1'
                   #nrows= 3000
)


#st.dataframe(df)
#para correar tu web app
# streamlit run app.py

#usa folium nomas

lat = list(df.LATITUD)
lon = list(df.LONGITUD)
cpue = list(df.captura_kg)

#FILTROS

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
year = st.sidebar.multiselect(
    "Selecciona el año:",
    options=df["year"].unique(),
    default=2015
)

tipo = st.sidebar.multiselect(
    "Selecciona el tipo de flota:",
    options=df["tipo"].unique(),
    default="Tipo I",
)

season = st.sidebar.multiselect(
    "Selecciona la estacion:",
    options=df["season"].unique(),
    default=df["season"].unique()
)

df_selection = df.query(
    "year == @year & tipo ==@tipo & season == @season"
)



#MAINPAGE
st.markdown("<h1 style='text-align: center; font-weight: bold; color: black;'>Dosidicus gigas Dashboard</h1>", unsafe_allow_html=True)
st.markdown("##")

#kpi
mean_cpue= round((df_selection["CPUE"].mean()),1)
trips=len(df_selection)
total_cpue=int((df_selection["CPUE"].sum()))

col1, col2, col3= st.columns(3)
col1.metric("CPUE Promedio: ", f"{mean_cpue} t")
col2.metric("Numero de viajes: ", f"{trips} trips")
col3.metric("CPUE Total (suma): ", f"{total_cpue} t")

st.markdown("---") #linea de separacion



#mainpage
df_month= df_selection.groupby(["month"]).mean()

col1,col2 = st.columns(2)
with col1:
    fig1 = px.line(df_selection, x='date', y="CPUE" , labels={
                     "date": "Fecha",
                     "CPUE": "CPUE (t/viaje)" } )
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
with col2:
    fig2 = px.line(df_month, x=None, y="CPUE")
    fig2.update_layout(title_text='CPUE promedio mensual', title_x=0.4,
                       xaxis_title="Mes", yaxis_title="CPUE (t/viaje)")
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)


#season
df_season= df_selection.groupby(["season"]).mean()
cantidad= df_selection["season"].value_counts().to_frame()

col1,col2 = st.columns(2)
with col1:
    bar1 = px.bar( 
    cantidad,x=None,y="season" 
)
    bar1.update_layout(title_text='Numero de viajes por estacion', title_x=0.4,
                       xaxis_title="Estacion", yaxis_title="Numero de viajes")
    st.plotly_chart(bar1, theme="streamlit", use_container_width=True)

with col2:
    bar2 = px.bar(
    df_season,
    x=None,
    y="CPUE",
    color="Sal_55m", color_continuous_scale="jet")
    bar2.update_layout(title_text='CPUE (t/viaje) promedio estacional', title_x=0.4,
                       xaxis_title="Estacion", yaxis_title="CPUE (t/viaje)")
    st.plotly_chart(bar2, theme="streamlit", use_container_width=True)


#escala colores cpue
import branca.colormap as cm
escala= ["#B5E384", "#FFFFBD",  "#FFAE63", "#D61818" , "red", "darkred"]

colormap = cm.LinearColormap(colors= ["yellow", "red"] , vmin=min(df_selection["CPUE"]), vmax=max(df_selection["CPUE"]), 
                            )

#mapa
m=leafmap.Map(center=[-15, -72], zoom=5,
fullscreen_control=False,
attribution_control=True)
m.add_tile_layer(
url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
name="Google Satellite",
attribution="Google",
)
    
# Agregar la posición del mouse en el mapa
MousePosition().add_to(m)
m.add_title("Distribucion CPUE (t/viaje)", font_size="20px", align="center")    
    
for loc, p in zip(zip(list(df_selection["LATITUD"]), list(df_selection["LONGITUD"])), 
                      list(df_selection["CPUE"])):
    folium.Circle(
    location=loc,
    radius=16,
    fill=True,
    color=colormap(p),
    popup=[loc,p]
    #fill_opacity=0.7
).add_to(m)

   
m.add_colorbar(colors=escala,vmin=min(df_selection["CPUE"]), vmax=max(df_selection["CPUE"]), transparent_bg=False , 
                             )
m.to_streamlit(height=500)




# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



