from typing import Text
import dash #manuseio do dashboard
import dash_core_components as dcc #criar componentes uteis 
import dash_html_components as html

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import geojson

import plotly.express as px 
import plotly.graph_objects as go 

import numpy as np 
import pandas as pd 
import json
from geojson import Feature, FeatureCollection, Point
from urllib.request import urlopen
#------------------------------------

df = pd.read_csv(
    r'C:\Users\xdead\Desktop\Projects\dashboards_ic\flood_dash.csv')
    
#print(df)
df1=df[['LAT', 'LONG']].astype(str)

#features = df1.apply(
 #   lambda row: Feature(geometry=Point(
  #      (float(row['LAT']), float(row['LONG'])))),
   # axis=1).tolist()
def f(x):
    return {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Point",
        "coordinates": x[["LAT", "LONG"]].values.tolist()
      }}
z=f(df1)

df1.to_csv('df1.csv', index="False")
map1 = json.load(open('df1.geojson', 'r'))
i = 1
for feature in map1["features"]:
    feature['id'] = str(i).zfill(2)
    i += 1
df_tweet=pd.read_csv(r'C:\Users\xdead\Desktop\Projects\dashboards_ic\tweet_pluvio_radar_flood.csv')

select_columns={"p3": "Medida Radar",
                    "Flood Frequence": "Frequência de alagamentos",
                    "valorMedida": "Valor do Pluviômetro",
                    "Tweet Frequence": "Frequência de Tweets"}


#-------------app-------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
#center = {"lat": -23.54940, "lon": -46.638806}
fig = px.scatter_mapbox(df,
                     lat=df.LAT,
                     lon=df.LONG,
                     hover_name="LOCAL_ED",
                     center = {"lat": -23.54940, "lon": -46.638806},
                     zoom=13.5,
                     color="DUR_H",
                     text='DATA',
                     size_max=10
                     )

fig.update_layout(mapbox_style="carto-darkmatter",
paper_bgcolor="#242424",
autosize=True,
margin=go.Margin(l=0, r=0,t=0,b=0),
showlegend=False)
####### importando o arquivo quantitativo

fig2=go.Figure()
fig2.add_trace(go.Bar(x=df_tweet['Date'],y=df_tweet["Flood Frequence"], text=df_tweet["Flood Frequence"]))
fig2.update_layout(paper_bgcolor="#242424",
                   plot_bgcolor="#242424",
                  autosize=True,
                   margin=dict(l=10, r=10, t=10, b=10))
fig2.update_traces(marker_color='rgb(0,255,255)', marker_line_color='rgb(8,48,107)',
                   marker_line_width=1.5, opacity=0.6, textposition='outside')
fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=False)


#-------------layout-------------------------

app.layout = dbc.Container(
    dbc.Row([
    dbc.Col([   
        html.Div([
            html.Img(id='logo', src=app.get_asset_url('cemaden.png'), height=70, width=100),
            html.H4("Alagamentos e mineração de dados - CEMADEN"),
            html.H5("Dashboard - Projeto IC - Vitor Y"),
            dbc.Button("São Paulo", color='Primary', id='location-button', size='lg')
        ], style={"margin-top": "40px"}),
        html.P("Informe", style={"margin-top":"40px"}),
        html.Div(id='div-test', children=[dcc.DatePickerSingle(
            id="date-picker", min_date_allowed=df_tweet["Date"].min(),
            max_date_allowed=df_tweet["Date"].max(),
            initial_visible_month=df_tweet["Date"].min(),
            date=df_tweet["Date"].max(), style={"border": "0px solid black"}, 
        )
        ]),
        dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Frequência de alagamentos"),
                            html.H3(style={"color": "#adfc92"}, id="alagamentos-text"),
                            html.Span("Duração total"),
                            html.H5(id="duracao-text"),
                        ])
                    ], color="light", outline= True, style={"margin-top":"10px", 
                    "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba (0,0,0,0.19)", 
                    "color": "#FFFFFF"},
                    )
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Valor de pluviômetro"),
                            html.H3(style={"color": "#389fd6"},
                                    id="pluvio-text"),
                            html.Span("Pluviômetro"),
                            html.H5(id="pluvio-tipo-text"),
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                           "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba (0,0,0,0.19)",
                                                           "color": "#FFFFFF"},
                    )
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Frequência de tweets"),
                            html.H3(style={"color": "#389fd6"},
                                    id="tweets-text"),
                            html.Span("Valor detectado pelo radar"),
                            html.H5(id="radar-text"),
                        ])
                    ], color="light", outline=True, style={"margin-top": "10px",
                                                           "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba (0,0,0,0.19)",
                                                           "color": "#FFFFFF"},
                    )
                ], md=4)
        ]),
        html.Div([
            html.P("Selecione o tipo de dado",
                   style={"margin-top": "25px"}),
            dcc.Dropdown(id="location-dropdown",
            options=[{"label": j, "value": i} for i, j in select_columns.items()],
            value="Tweet Frequence",
            style={"margin-top": "10px"}),
            dcc.Graph(id='bar-chart', figure=fig2)
        ]),
        ], md=5, style={"padding": "25px", "background-color": "#242424"}),
        dbc.Col([
            dcc.Loading(id="loadin-1", type="default", children=[ 
            dcc.Graph(id='choropleth-map', figure=fig, style={'height':"100vh", 'margin_right':'10px'})
            ])
        ], md=7)
    ], className="g-0"), 
    fluid=True)

#interatividade
@app.callback([Output("alagamentos-text", "children"),
               Output("pluvio-text", "children"),
               Output("radar-text", "children"),
               Output("duracao-text", "children"),
               Output("tweets-text", "children"),
               Output("pluvio-tipo-text", "children")],
[Input("date-picker", "date"), Input("location-button", "children")])
def display_status(date, location):
    tweets=df_tweet[df_tweet['Date']==date]["Tweet Frequence"].values
    alagamentos=df_tweet[df_tweet['Date']==date]["Flood Frequence"].values
    pluvio=df_tweet[df_tweet['Date']==date]["valorMedida"].values
    radar = df_tweet[df_tweet['Date'] == date]["p3"].values
    duracao=str('--')
    tipo_pluvio=str('833A')
    return(alagamentos,pluvio,radar,duracao,tweets,tipo_pluvio)


@app.callback(Output('bar-chart', 'figure'), Input("location-dropdown", 'value'))
def plot_scater_graph(plot_type):
    fig2=go.Figure(layout={"template": "plotly_dark"})
    fig2.add_trace(go.Bar(x=df_tweet['Date'], y=df_tweet[plot_type], text=df_tweet["Date"]))
    fig2.update_layout(paper_bgcolor="#242424",
                       plot_bgcolor="#242424",
                       autosize=True,
                       margin=dict(l=10, r=10, t=10, b=10))
    fig2.update_traces(marker_color='rgb(0,255,255)', marker_line_color='rgb(8,48,107)',
                   marker_line_width=1.5, opacity=0.6, textposition='outside')
    fig2.update_xaxes(showgrid=False)
    fig2.update_yaxes(showgrid=False)
    return fig2
if __name__ == "__main__":
    app.run_server(debug=True)
