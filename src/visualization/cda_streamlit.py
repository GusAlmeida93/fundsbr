import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
from pathlib import Path


full_path = Path(__file__).parent.absolute().parent.absolute()
directory = f'{Path(full_path).parent}/data/processed'

funds = pd.read_csv(f'{directory}/funds.csv', sep = ';', encoding = 'latin1', decimal=',')

@st.cache
def sankey(funds, fund):

    
    
    df = funds[funds['NM_FUNDO_COTA'] == fund][['CNPJ_FUNDO', 'DENOM_SOCIAL', 'VL_MERC_POS_FINAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].reset_index(drop = True)

    funds_searched = [fund]

    funds_search = list(df['DENOM_SOCIAL'].unique())


    while funds_search:

        df_search = funds[funds['NM_FUNDO_COTA'].isin(funds_search)][['CNPJ_FUNDO', 'DENOM_SOCIAL', 'VL_MERC_POS_FINAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].reset_index(drop = True)

        funds_searched = funds_searched + funds_search

        funds_search = list(df_search['DENOM_SOCIAL'].unique())


        funds_search = set(funds_search) - set(funds_searched)

        funds_search = list(funds_search)



        df = pd.concat([df_search, df])
        
    dim_sankey = pd.concat([df[['CNPJ_FUNDO', 'DENOM_SOCIAL']], df[['CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].rename(columns={'CNPJ_FUNDO_COTA' : 'CNPJ_FUNDO', 'NM_FUNDO_COTA' : 'DENOM_SOCIAL'})]).drop_duplicates().reset_index(drop = True).reset_index()
    
    df = df.merge(dim_sankey, left_on='CNPJ_FUNDO', right_on='CNPJ_FUNDO').rename(columns={'index' : 'index_source'})
    df = df.merge(dim_sankey, left_on='CNPJ_FUNDO_COTA', right_on='CNPJ_FUNDO').rename(columns={'index' : 'index_target'}).drop(columns=['CNPJ_FUNDO_y'], axis=1).rename(columns={'CNPJ_FUNDO_x' : 'CNPJ_FUNDO'})
    
    source = df['index_source']
    target = df['index_target']
    value = df['VL_MERC_POS_FINAL']
    label = dim_sankey['DENOM_SOCIAL']

    return source, target, value, label


    

fund = st.sidebar.selectbox('Fundos', sorted(funds['NM_FUNDO_COTA'].unique()))

source, target, value, label = sankey(funds, fund)

fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",

    node = dict(
      pad = 15,
      thickness = 15,
      line = dict(color = "black", width = 0.5),
      label =  label
    ),
    # Add links
    link = dict(
      source =  source,
      target =  target,
      value =  value
))])

fig.update_layout(title_text="CDA", font_size=10, width = 800, height = 600)
st.plotly_chart(fig)


