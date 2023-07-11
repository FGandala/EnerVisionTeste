import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import geopandas as gpd
import altair as alt

st.set_page_config(page_title='Forecasting',layout='wide')

pagina = st.empty()
@st.cache_data
def coleta_dados_csv():
  dados=pd.read_csv('DadosFiltrados.csv')
  return dados


@st.cache_data
def coleta_localizacao():
  localizacao = gpd.read_file('grandes_regioes_json.geojson')
  return localizacao
def filtra_dados(região,tempo_inicial,tempo_final):
  tempo_inicial=datetime.datetime(tempo_inicial.year,tempo_inicial.month,tempo_inicial.day,0,0,0)
  tempo_final=datetime.datetime(tempo_final.year,tempo_final.month,tempo_final.day,23,0,0)
  data_frame=coleta_dados_csv()
  dados = data_frame[[região,'Datetime']]
  dados['Datetime']=pd.to_datetime(dados['Datetime'])
  if tempo_inicial.year != tempo_final.year:
    a=1
  elif tempo_inicial.month != tempo_final.month:
    a=2
  elif tempo_inicial.day != tempo_final.day: 
    a=3
  else:
    filtrados=dados.loc[(dados['Datetime']>=tempo_inicial)&(dados['Datetime']<=tempo_final)]
    filtrados['Datetime']=filtrados['Datetime'].apply(lambda x:pd.to_timedelta(x.hour,unit='h'))
    st.write(filtrados)
    return filtrados
def cria_grafico_linhas(dados,região):
  
  grafico=alt.Chart(dados).mark_area(color = 'orange',
                           opacity = 0.5, line = {'color':'orange'}).encode(
    alt.X('Datetime:T'),
    alt.Y(região)).properties(
    width=1000,
    height=700).configure_axis(labelLimit=250,labelFontSize=30,grid=True,title=None)
  st.subheader("Demanda Prevista")
  return grafico
  

@st.cache_data(experimental_allow_widgets=True)
def cria_mapa(cores):

    dados=coleta_dados_csv()
    carga_estados={'Estados':[],
               'Mhw':[]}
    estados=['Nordeste','Norte','Sul','Centro-sul']
    for i in estados:
      carga_estados['Estados'].append(i)
      carga_estados['Mhw'].append(dados[i].iloc[-24::].sum().round())

    carga_estados=pd.DataFrame(carga_estados)
    mapa = folium.Map(location=[-14.235,-54.2],zoom_start=4,
                    max_zoom=4,min_zoom=4,tiles='CartoDB positron',dragging=False,prefer_canvas=True)
  
    carga_estados['cores']=cores
          
    cloropleth = folium.Choropleth(
        geo_data=coleta_localizacao(),
        data=carga_estados,
        columns=['Estados','cores'],
        key_on='feature.properties.NOME2',
        fill_color='Spectral'
        )
    carga_estados.set_index('Estados',inplace=True)
    cloropleth.geojson.add_to(mapa)
    for features in cloropleth.geojson.data['features']:
        features['properties']['MHW'] = "Consumo nas últimas 24 horas: "+ str(carga_estados.loc[features['properties']['NOME2']]['Mhw'])+' Mhw'
          
    cloropleth.geojson.add_child(
          folium.features.GeoJsonTooltip(['NOME2','MHW'],labels=False)
        )
    st.subheader("Região Selecionada")
    st_mapa = st_folium(mapa, width=1000, height=450,key='Centro-sul') 
    
          
def home():
    
  
    st.sidebar.image('LOGO.png')

    opção_regiao = st.sidebar.selectbox('Escolha uma região',('Norte','Nordeste','Centro-sul','Sul')) 
    if opção_regiao == 'Centro-sul':
      cria_mapa([None,None,None,200])
    if opção_regiao == 'Nordeste':
      cria_mapa([200,None,None,None])
    if opção_regiao == 'Norte':
      cria_mapa([None,200,None,None])
    if opção_regiao == 'Sul':
      cria_mapa([None,None,200,None])
    dados_tempo=coleta_dados_csv()
    inicio=pd.to_datetime(dados_tempo['Datetime']).iloc[0]
    fim=pd.to_datetime(dados_tempo['Datetime']).iloc[len(dados_tempo['Datetime'])-1]
    opção_tempo_inicial = st.sidebar.date_input('Escolha uma data inicial',fim,min_value=inicio,
                                              max_value=fim,
                                              )
    
    
  
    opção_tempo_final = st.sidebar.date_input('Escolha uma data final',opção_tempo_inicial,min_value=opção_tempo_inicial,
                                              max_value=fim,
                                              )

    
    
    st.altair_chart(cria_grafico_linhas(filtra_dados(opção_regiao,opção_tempo_inicial,opção_tempo_final),opção_regiao), theme="streamlit", use_container_width=True)







home()
  
