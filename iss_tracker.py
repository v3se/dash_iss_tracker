import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import urllib.request, json
import plotly.graph_objs as go
import ephem
import datetime
import math

tle_name = 'ISS (ZARYA)';
tle_element_url = 'http://www.celestrak.com/NORAD/elements/stations.txt'

#tle_rec = ephem.readtle(name, line1, line2)
#tle_rec.compute()


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
    #print(data)

    layout = dict(
        title = 'ISS Location',
        autosize=True,
        width=1200,
        height=800,
#        margin=go.layout.Margin(
#        l=10,
#        r=10,
#        b=1,
#        t=10,
#        pad=1
    
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
#fig = tools.make_subplots(rows=3, cols=1, layout=layout, specs=[[{}], [{}]])


app.layout  = html.Div([
	html.Div([
    dcc.Graph(id='graph', figure=fig),
    dcc.Interval(
        id='interval-component',
        interval=1*5000, # in milliseconds
        n_intervals=0
        )], style={'display': 'inline-block'}),
		html.Div([
		html.P(html.Iframe(src="https://www.ustream.tv/embed/9408562?html5ui", width="700", height="500", title="ISS Live Feed"))
		], style={'marginBottom': 1, 'marginTop': 1, 'position': 'relational', 'right': 100, 'top': 140, 'float': 'right', 'display': 'inline-block'})

])




@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='interval-component', component_property='n_intervals')])

def update_value(interval):
    f = urllib.request.urlopen('http://www.celestrak.com/NORAD/elements/stations.txt')
    myfile = f.read()
    arr = myfile.decode().split("\r")
    #print ("result code: " + str(f.getcode()))
    tle_line1 = arr[1]
    tle_line2 = arr[2]
    #print (tle_line1,tle_line2)
    date = datetime.datetime.utcnow()
    tick = datetime.timedelta(0,300)
    date_n = date + datetime.timedelta(0,5400)
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    for i in range(18):
        date = date + tick
        tle_rec = ephem.readtle(tle_name, tle_line1, tle_line2)
        tle = tle_rec.compute(date)
        lon_deg= math.degrees(tle_rec.sublong)
        lat_deg = math.degrees(tle_rec.sublat)
        #print(tle_rec.sublong, tle_rec.sublat, lon_deg, lat_deg)
        df = pd.DataFrame(data={'lon': [lon_deg], 'lat': [lat_deg], 'time': [date]})
        df2 = df2.append(df)
        
    #print (df2)

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
        hovertext = 'ISS Realtime Location'),
        go.Scattergeo(
        lon = df2.lon,
        lat = df2.lat,
        name = 'ISS Orbit (+5min - +90min)',
        mode = 'lines',
        opacity = 0.5,
        hovertext = df2.time,
        line = go.scattergeo.Line(
            width = 2.5,
            color = 'blue',))]

        fig=go.Figure(data=data, layout=layout)
        #fig.append_trace({'x':df2.lon,'y':df2.lat,'type':'scatter','name':'orbit'},1,1)

        return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
