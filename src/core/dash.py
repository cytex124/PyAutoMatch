# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from .db import Person
from pony.orm import db_session, select


@db_session
def get_data(group_by):
    counter = {}
    for p in select(p for p in Person):
        group = eval('p.{}'.format(group_by))
        if group not in counter:
            counter[group] = {}
            counter[group]['likes'] = 1
            counter[group]['matches'] = 0
        else:
            counter[group]['likes'] += 1
        if p.is_matched:
            counter[group]['matches'] += 1
    return counter


@db_session
def generate_table():
    groups = get_data('country')
    for group_name in groups.keys():
        groups[group_name]['quote'] = '{0:.2f}%'.format(groups[group_name]['matches'] / groups[group_name]['likes'] * 100)
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in ['country', 'likes', 'matches', 'quote']])] +

        # Body
        [html.Tr([
            html.Td(i)
                 ]+[
            html.Td(groups[i][col]) for col in ['likes', 'matches', 'quote']
        ]) for i in groups.keys()]
    )



external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Tinder Stats'
app.layout = html.Div(children=[
    html.H1(children='Tinder Stats', style={'text-align': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': i, 'value': i} for i in ['country', 'city']],
            value='country'
        )
    ], style={'width': '20%', 'display': 'inline-block'}),
    dcc.Graph(
        id='tinder-counter',
        figure={
            'data': [],
            'layout': {
                'title': 'Tinder Matches'
            }
        }
    ),
    generate_table()
])


def get_data_for_graph(group_by='country'):
    counter = get_data(group_by)
    data = [
        {'type': 'bar', 'name': 'Likes', 'x': [x for x in counter.keys()], 'y': [counter[y]['likes'] for y in counter]},
        {'type': 'bar', 'name': 'Matches', 'x': [x for x in counter.keys()],
         'y': [counter[y]['matches'] for y in counter]},
    ]
    return data


@app.callback(
    dash.dependencies.Output('tinder-counter', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value')]
)
def update_output(value):
    return {'data': get_data_for_graph(value)}


def run_dash_server():
    app.run_server(debug=True)
