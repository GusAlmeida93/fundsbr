import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import base64


full_path = Path(__file__).parent.absolute().parent.absolute()
directory = f'{Path(full_path).parent}/data/processed'

cda_fundos = pd.read_csv(f'{directory}/cda_fundos.csv', sep = ';', encoding = 'latin1', decimal=',')
admin = pd.read_parquet(f'{directory}/dim_administrador.parquet')
fundos = pd.read_parquet(f'{directory}/dim_fundos.parquet')
gestor = pd.read_parquet(f'{directory}/dim_gestor.parquet')
tipo = pd.read_parquet(f'{directory}/dim_tipo_fundo.parquet')
mvt = pd.read_parquet(f'{directory}/fato_movimento_detalhado.parquet')

fundos['fundo_cnpj'] = pd.to_numeric(fundos['fundo_cnpj'])

opacity_node = 1

colors_node = {"Multimercados" : f"rgba(252, 157, 23, {opacity_node})",
               "Ações": f"rgba(76, 77, 79, {opacity_node})",
               "Renda Fixa" : f"rgba(0, 149, 217, {opacity_node})",
               "Cambial" : f"rgba(102, 105, 122, {opacity_node})",
               "Previdência" : f"rgba(128, 195, 66, {opacity_node})",
               "FIP" : f"rgba(255, 223, 79, {opacity_node})",
               "FIDC" : f"rgba(191, 215, 48, {opacity_node})",
               "ETF"  : f"rgba(222, 118, 28, {opacity_node})",
               "FII" : f"rgba(3, 191, 215, {opacity_node})"
               }

opacity_link = 0.4
colors_link = {"Multimercados" : f"rgba(252, 157, 23, {opacity_link})",
               "Ações": f"rgba(76, 77, 79, {opacity_link})",
               "Renda Fixa" : f"rgba(0, 149, 217, {opacity_link})",
               "Cambial" : f"rgba(102, 105, 122, {opacity_link})",
               "Previdência" : f"rgba(128, 195, 66, {opacity_link})",
               "FIP" : f"rgba(255, 223, 79, {opacity_link})",
               "FIDC" : f"rgba(191, 215, 48, {opacity_link})",
               "ETF"  : f"rgba(222, 118, 28, {opacity_link})",
               "FII" : f"rgba(3, 191, 215, {opacity_link})"
               }


def get_table_download_link(df,name):
  
    csv = df.to_csv(index=False, sep = ";", decimal = ',', encoding = 'latin1')
    b64 = base64.b64encode(csv.encode('latin1')).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{name}.csv">Download dados</a>'
    
    return href

@st.cache
def sankey(cda_fundos, fund, fundos, colors_node, colors_link):

    df = cda_fundos[cda_fundos['NM_FUNDO_COTA'] == fund][['CNPJ_FUNDO', 'DENOM_SOCIAL', 'VL_MERC_POS_FINAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].reset_index(drop = True)
    
    df = df.groupby(by = ['CNPJ_FUNDO', 'DENOM_SOCIAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA'], as_index = False).sum()
    
    funds_searched = [fund]

    funds_search = list(df['DENOM_SOCIAL'].unique()) # type: ignore

    count = 1
    nivel = {}

    while funds_search:

        nivel[count] = funds_search.copy()
        
        df_search = cda_fundos[cda_fundos['NM_FUNDO_COTA'].isin(funds_search)][['CNPJ_FUNDO', 'DENOM_SOCIAL', 'VL_MERC_POS_FINAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].reset_index(drop = True)
        df_search = df_search.groupby(by = ['CNPJ_FUNDO', 'DENOM_SOCIAL', 'CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA'], as_index = False).sum()

        funds_searched = funds_searched + funds_search

        funds_search = list(df_search['DENOM_SOCIAL'].unique())
        
        

        funds_search = set(funds_search) - set(funds_searched)

        funds_search = list(funds_search)
        
        df = pd.concat([df_search, df])
        
        count += 1
        
    dim_sankey = pd.concat([df[['CNPJ_FUNDO', 'DENOM_SOCIAL']], df[['CNPJ_FUNDO_COTA', 'NM_FUNDO_COTA']].rename(  
      columns={'CNPJ_FUNDO_COTA' : 'CNPJ_FUNDO', 'NM_FUNDO_COTA' : 'DENOM_SOCIAL'})]).drop_duplicates().reset_index(drop = True).reset_index()  # type: ignore
    
    df['nivel'] = df.apply(lambda x: [idx for idx, item in nivel.items() if x['DENOM_SOCIAL'] in item][0] , axis = 1 ) 
    
    dim_sankey = dim_sankey.merge(fundos[['fundo_cnpj', 'fundo_codigo', 'fundo_fantasia']], left_on='CNPJ_FUNDO', right_on = 'fundo_cnpj').drop(columns = ['fundo_cnpj'])
    dim_sankey = dim_sankey.merge(mvt, on = 'fundo_codigo')
    dim_sankey = dim_sankey.merge(tipo[['tipo_fundo_codigo','tipo_fundo_classe_anbima_n1']], left_on = 'codtipo', right_on = 'tipo_fundo_codigo').drop(columns = ['tipo_fundo_codigo'])
    dim_sankey = dim_sankey.merge(admin[['administrador_codigo', 'administrador_mae_codigo_fantasiac']], left_on = 'codadm', right_on = 'administrador_codigo').drop(columns = ['administrador_codigo'])
    dim_sankey = dim_sankey.merge(gestor[['gestor_codigo', 'gestor_mae_codigo_fantasiac']], left_on = 'codgestor', right_on = 'gestor_codigo').drop(columns = ['gestor_codigo'])
    dim_sankey['label'] = ''
    dim_sankey = dim_sankey.sort_values(by = ['index'])
    
    
    df = df.merge(dim_sankey, left_on='CNPJ_FUNDO', right_on='CNPJ_FUNDO').rename(columns={'index' : 'index_source'})
    df = df.merge(dim_sankey, left_on='CNPJ_FUNDO_COTA', right_on='CNPJ_FUNDO').rename(columns={'index' : 'index_target'})

    df = df.rename(columns = {'tipo_fundo_classe_anbima_n1_x' : 'tipo_fundo_classe_anbima_n1' })
    
    df['composicao'] = df.apply(lambda x: round((x['VL_MERC_POS_FINAL'] / df[df['CNPJ_FUNDO_y'] == x['CNPJ_FUNDO_y']]['VL_MERC_POS_FINAL'].sum()), 2) , axis = 1)
    
    
    dim_sankey['customdata'] = dim_sankey.apply(lambda x: f'''Administrador: {x["administrador_mae_codigo_fantasiac"]}<br />Gestor: {
                                                          x["gestor_mae_codigo_fantasiac"]}<br />Fundo: {x["fundo_fantasia"]}<br />Tipo: {
                                                          x["tipo_fundo_classe_anbima_n1"]}<br />Composição: {df[df["CNPJ_FUNDO_y"] == x["CNPJ_FUNDO"]][["DENOM_SOCIAL_x", 'composicao']].sort_values(by=['composicao'], ascending=False).values.tolist() }''', axis = 1) # type: ignore
    
    dim_sankey['customdata'] = dim_sankey['customdata'].str.replace('],', '<br />')
    dim_sankey['customdata'] = dim_sankey['customdata'].str.replace('[', '') # type: ignore
    dim_sankey['customdata'] = dim_sankey['customdata'].str.replace(']', '')
    dim_sankey['customdata'] = dim_sankey['customdata'].str.replace(',', ':')
    dim_sankey['customdata'] = dim_sankey['customdata'].str.replace("'", '')
    dim_sankey['color'] = dim_sankey.apply(lambda x: colors_node[x['tipo_fundo_classe_anbima_n1']], axis = 1)
    
    dim_sankey = dim_sankey.set_index('index')
    
    
    df['customdata'] = df.apply(lambda x: f'De: {x["DENOM_SOCIAL_x"]}<br />Para: {x["DENOM_SOCIAL"]}', axis = 1)
    df['color'] = df.apply(lambda x: colors_link[x['tipo_fundo_classe_anbima_n1']], axis = 1)
    
    source = df['index_source']
    target = df['index_target']
    value = df['VL_MERC_POS_FINAL']
    label = dim_sankey['label']
    node_customdata = dim_sankey['customdata']
    link_customdata = df['customdata']
    node_color = dim_sankey['color']
    link_color = df['color']
    

    df = df[['nivel', 'CNPJ_FUNDO_x', 'DENOM_SOCIAL_x', 'VL_MERC_POS_FINAL','CNPJ_FUNDO_y', 'DENOM_SOCIAL_y', 'composicao']]
    
    dim_sankey = dim_sankey[['CNPJ_FUNDO', 'DENOM_SOCIAL', 'fundo_codigo', 'fundo_fantasia', 'codadm', 'codtipo', 'codgestor', 'tipo_fundo_classe_anbima_n1', 'administrador_mae_codigo_fantasiac']] 


    return source, target, value, label, node_customdata, link_customdata, node_color, link_color, df, dim_sankey, nivel


    
st.title('Análise da Árvore dos Fundos utilizando o Sankey Diagram')

fund = st.sidebar.selectbox('Fundos', sorted(cda_fundos['NM_FUNDO_COTA'].unique()))

st.subheader(f'Sankey Diagram')

source, target, value, label, node_customdata, link_customdata, node_color, link_color, df, dim_sankey, nivel = sankey(cda_fundos, fund, fundos, colors_node, colors_link) # type: ignore

fig = go.Figure(data=[go.Sankey( # type: ignore
    valueformat = "000,000.0f",    

    node = dict(
      pad = 15,
      thickness = 15,
      line = dict(color = "black", width = 0.5),
      label =  label,
      customdata = node_customdata,
      hoverinfo = 'all',
      hovertemplate = '%{customdata}' + '<br />Valor: %{value}<extra></extra>',
      color = node_color
    ),
    # Add links
    link = dict(
      source =  source,
      target =  target,
      value =  value,
      customdata = link_customdata,
      hovertemplate = '%{customdata}' + '<br />Valor: %{value}<extra></extra>',
      color = link_color
  
    ),
      
    )])

fig.update_layout(title_text= fund, font_size=10, width = 800, height = 600)
st.plotly_chart(fig)


st.subheader('Fato')
st.dataframe(df)
st.markdown(get_table_download_link(df, 'Fato'), unsafe_allow_html=True)

st.subheader('Dimensão')
st.dataframe(dim_sankey)
st.markdown(get_table_download_link(dim_sankey, 'Dimensão'), unsafe_allow_html=True)






st.balloons()




