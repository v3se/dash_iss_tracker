import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import urllib.request, json
import plotly.graph_objs as go


iss_url = 'http://api.open-notify.org/iss-now.json'

app = dash.Dash()

with urllib.request.urlopen(iss_url) as url:
    data = json.loads(url.read().decode())
    lat = data['iss_position']['latitude']
    lon = data['iss_position']['longitude']
    d = {'lon': [lon], 'lat': [lat]}
    df = pd.DataFrame(data=d)
    data = [ go.Scattergeo(
    lon = df['lon'],
    lat = df['lat'])]

    layout = dict(
        title = 'ISS Location',
        autosize=False,
        width=1250,
        height=1250,
        margin=go.layout.Margin(
        l=80,
        r=50,
        b=400,
        t=100,
        pad=4
    ),
        geo = dict(
            scope='world',
            projection=dict( type='robinson' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 1,
            subunitwidth = 1
        ),
    )


fig=go.Figure(data=data, layout=layout)

app.layout  = html.Div([
    dcc.Graph(id='graph', figure=fig),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
        )
])

@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='interval-component', component_property='n_intervals')])

def update_value(interval):
    with urllib.request.urlopen(iss_url) as url:
        data = json.loads(url.read().decode())
        lat = data['iss_position']['latitude']
        lon = data['iss_position']['longitude']
        d = {'lon': [lon], 'lat': [lat]}
        df = pd.DataFrame(data=d)
        data = [ go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        name = 'ISS',
        marker = dict(symbol='circle', size = 10, opacity = 0.7, color = "red"),
        hovertext = 'ISS Realtime Location')]
        fig=go.Figure(data=data, layout=layout)

        return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
