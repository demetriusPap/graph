import os
import newdata as db
import requests as req
import urllib3
from datetime import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start ='1561939200' #	Datetime to specify the start of the exported data, in Unix timestamp.DEFAULT is 'NOW - 24 Hours'
serverName='testnagios'
hostName = '172.16.10.96'
serviceDescription = 'FastEthernet0/0 LAN Bandwidth'

timebw=[]
inbw=[]
outbw=[]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

serverName = 'testnagios'
url = 'https://' + db.serverList[serverName]['ip'] + '/nagiosxi/api/v1/objects/rrdexport?apikey=' + \
          db.serverList[serverName]['apikey']+'&host_name='+ hostName+'&service_description=' + serviceDescription#+'&start='+start

response = req.get(url, verify=False).json() #use for loop inside update_graph_live() if you want an update every 5 mins. Beware that the exexution might get significantly slower!
for i in range(288):
    timebw.append(datetime.fromtimestamp(int(response['data']['row'][i]['t'])))
    inbw.append(float(response['data']['row'][i]['v'][0]))
    outbw.append(float(response['data']['row'][i]['v'][1]))


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Bandwidth'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=300*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):

    """response = req.get(url, verify=False).json()
    for i in range(288):
        timebw.append(datetime.fromtimestamp(int(response['data']['row'][i]['t'])))
        inbw.append(float(response['data']['row'][i]['v'][0]))
        outbw.append(float(response['data']['row'][i]['v'][1]))"""

    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
            'x': timebw,
            'y': inbw,
            'name': 'Bandwidth/In',
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)
    fig.append_trace({
            'x': timebw,
            'y': outbw,
            'name': 'Bandwidth/Out',
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 2, 1)

    if not os.path.exists("images"):
        os.mkdir("images")
    fig.write_image("images/bwgraphs.png")

    if not os.path.exists("HTML"):
        os.mkdir("HTML")
    plotly.offline.plot(fig, filename='HTML/Bandwidth_Graph.html')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
