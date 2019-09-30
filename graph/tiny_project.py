import datetime
#import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import re
import netmiko
import newdata as db
import plotly.graph_objs as go



command = 'ping -c 1 172.16.10.96'

serverName='testnagios'





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Ping'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=9000, # in milliseconds
            n_intervals=0
        )
    ])
)



# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):

    data = {
        'time': [],
        'ping': []
    }

    session = connectSSH(serverName)



    response = session.send_command(command)
    times = re.findall('\d+ bytes from \d+\.\d+\.\d+\.\d+: icmp_seq=[0-9]+ ttl=\d+ time=(\d+\.\d+) ms', response)
    for result in times:
        data['ping'].append(result)



        #time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
        #ping = random.randint(1,101)
        #data['ping'].append(ping)
        #data['time'].append(time)
    time = datetime.datetime.now() #- datetime.timedelta(seconds=i* 20)
    data['time'].append(time)
    #x = data['time']
    #y = data['ping']

    with open('response.txt', 'a') as f:
        #f.seek(0)
        #f.truncate() # !!!!!! replaces previous files
        for z, m in zip(data['ping'],data['time']):
            d=str(m)
            f.write('{},{}\n'.format(z, d))
            f.flush()

    graph_data = open('response.txt', 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            y, x = line.split(',')
            xs.append(str(x))
            ys.append(float(y))




    data = plotly.graph_objs.Scatter(
        #x=data['time'],
        #y=data['ping'],
        x=xs,
        y=ys,
        name='Scatter',
        mode='lines+markers'
    )
    x = xs
    y = ys
    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(x), max(x)]),
                                                yaxis=dict(range=[min(y), max(y)]), )}

    '''

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=1, cols=1)
    fig['layout']['margin'] = {
        'l': 50, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['ping'],
        'name': 'Ping',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig
    '''



def connectSSH(serverName):
    ''' Connects to a server via SSH

    :param serverName: Server ID
    :return: Netmiko Session
    '''
    session = netmiko.ConnectHandler(device_type='cisco_ios',
                                     ip=db.serverList[serverName]['ip'],
                                     username=db.serverList[serverName]['userSSH'],
                                     password=db.serverList[serverName]['passSSH'])
    return session


if __name__ == '__main__':
    app.run_server(debug=True)
    


