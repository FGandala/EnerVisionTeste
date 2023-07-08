import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly 
import plotly_express as px
import datetime
from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data
import json
import geopandas as gpd

st.set_page_config(page_title='Forecasting',layout='wide')
if 'estado_escolhido' not in st.session_state:
  st.session_state['estado_escolhido'] = 'Centro-sul'
pagina = st.empty()


DATA=('https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/carga_energia_di/CARGA_ENERGIA_2023.csv')
carga=pd.read_csv(DATA,delimiter=';')
carga.nom_subsistema = carga.nom_subsistema.apply(lambda x:'Centro-sul'if(x=='Sudeste/Centro-Oeste')
                                                  else x)

estados=['Nordeste','Norte','Sul','Centro-sul']
carga_estados={'Estados':[],
               'Mhw':[]}
for i in estados:
    carga_estados['Estados'].append(i)
    carga_estados['Mhw'].append((carga.loc[carga.nom_subsistema==i]['val_cargaenergiamwmed'].sum()))

carga_estados=pd.DataFrame(carga_estados)

@st.cache_data
def coleta_localizacao():
  localizacao = gpd.read_file('grandes_regioes_json.geojson')
  return localizacao

def filtra_dados(região):
  dados = pd.DataFrame(data=carga[carga['nom_subsistema']==região]['val_cargaenergiamwmed'].values,
                        index=carga[carga['nom_subsistema']==região]['din_instante'].values,
                        columns=['Carga'])
  return dados



def cria_grafico_linhas(dados_centro_sul):

  overlaidAreaSeriesOptions = {
    "height": 400,
    "rightPriceScale": {
        "scaleMargins": {
            "top": 0.1,
            "bottom": 0.1,
        },
        "mode": 2, # PriceScaleMode: 0-Normal, 1-Logarithmic, 2-Percentage, 3-IndexedTo100
        "borderColor": 'rgba(197, 203, 206, 0.4)',
    },
    "timeScale": {
        "borderColor": 'rgba(197, 203, 206, 0.4)',
    },
    "layout": {
        "background": {
            "type": 'solid',
            "color": '#100841'
        },
        "textColor": '#ffffff',
    },
    "grid": {
        "vertLines": {
            "color": 'rgba(197, 203, 206, 0.4)',
            "style": 1, # LineStyle: 0-Solid, 1-Dotted, 2-Dashed, 3-LargeDashed
        },
        "horzLines": {
            "color": 'rgba(197, 203, 206, 0.4)',
            "style": 1, # LineStyle: 0-Solid, 1-Dotted, 2-Dashed, 3-LargeDashed
        }
    }
}

  seriesOverlaidChart = [
    {
        "type": 'Area',
        "data": data.seriesMultipleChartArea01,
        "options": {
            "topColor": 'rgba(255, 192, 0, 0.7)',
            "bottomColor": 'rgba(255, 192, 0, 0.3)',
            "lineColor": 'rgba(255, 192, 0, 1)',
            "lineWidth": 2,
        },
        "markers": [
            {
                "time": '2019-04-08',
                "position": 'aboveBar',
                "color": 'rgba(255, 192, 0, 1)',
                "shape": 'arrowDown',
                "text": 'Pico',
                "size": 3
            },
            {
                "time": '2019-05-13',
                "position": 'belowBar',
                "color": 'rgba(255, 192, 0, 1)',
                "shape": 'arrowUp',
                "text": 'Demanda Próxima Hora',
                "size": 3
            },
        ]
    }
    
]
  st.subheader("Demanda Prevista")

  renderLightweightCharts([
    {
        "chart": overlaidAreaSeriesOptions,
        "series": seriesOverlaidChart
    }
], 'overlaid')

def cria_mapa():
    DATA=('https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/carga_energia_di/CARGA_ENERGIA_2023.csv')
    carga=pd.read_csv(DATA,delimiter=';')
    carga.nom_subsistema = carga.nom_subsistema.apply(lambda x:'Centro-sul'if(x=='Sudeste/Centro-Oeste')
                                                  else x)


    carga_estados={'Estados':[],
               'Mhw':[]}
    estados=['Nordeste','Norte','Sul','Centro-sul']
    for i in estados:
      carga_estados['Estados'].append(i)
      carga_estados['Mhw'].append((carga.loc[carga.nom_subsistema==i]['val_cargaenergiamwmed'].sum()))

    carga_estados=pd.DataFrame(carga_estados)
    mapa = folium.Map(location=[-14.235,-54.2],zoom_start=4,
                    max_zoom=4,min_zoom=4,tiles='CartoDB positron',dragging=False)

    if st.session_state.estado_escolhido == 'Centro-sul':
      carga_estados['cores']=[None,None,None,200]
          

    if st.session_state.estado_escolhido == 'Nordeste':
        carga_estados['cores']=[200,None,None,None]

        
    cloropleth = folium.Choropleth(
        geo_data=coleta_localizacao(),
        data=carga_estados,
        columns=['Estados','cores'],
        key_on='feature.properties.NOME2',
        fill_color='Spectral'
        )
    carga_estados.set_index('Estados',inplace=True)

    for features in cor_do_mapa.geojson.data['features']:
        features['properties']['MHW'] = "Carga diária" + " : " + str(carga_estados.loc[features['properties']['NOME2']]['Mhw'])
          
          
    cor_do_mapa.geojson.add_child(
          folium.features.GeoJsonTooltip(['NOME2','MHW'],labels=False)
        )
    st.subheader("Região Atual")
    st_folium(mapa, width=1000, height=450,feature_group_to_add=cor_do_mapa,
                         )
    if st_mapa['last_active_drawing']:
          st.session_state.estado_escolhido=st_mapa['last_active_drawing']['properties']['NOME2']
          return cria_mapa()
        



def home():

    st.sidebar.image('LOGO.png')
  
    opção_tempo_inicial = st.sidebar.date_input('Escolha um valor inicial',datetime.date(2023, 5, 6),min_value=datetime.date(2023, 1, 1),
                                              max_value=datetime.date(2023, 7, 3),
                                              )
    
  
    opção_tempo_final = st.sidebar.date_input('Escolha um valor final',datetime.date(2023, 5, 6),min_value=datetime.date(2023, 1, 1),
                                              max_value=datetime.date(2023, 7, 3),
                                              )
    
    cria_mapa()
    dados_centro_sul = filtra_dados(st.session_state.estado_escolhido)
    
  
    cria_grafico_linhas(dados_centro_sul)


home()
  
