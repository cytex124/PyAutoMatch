# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from .db import Person
from pony.orm import db_session, select


@db_session
def _get_tinderlike_data(group_by: str) -> dict:
    # Create counter obj
    counter = {}
    # GET all Persons you liked with the script
    for p in select(p for p in Person):
        # Order by group name
        group = eval('p.{}'.format(group_by))
        # Init group
        if group not in counter:
            counter[group] = {}
            counter[group]['likes'] = 1
            counter[group]['matches'] = 0
        # If inited just upgrade like
        else:
            counter[group]['likes'] += 1
        # If tinder-like matched you update +1
        if p.is_matched:
            counter[group]['matches'] += 1
    return counter


@db_session
def _generate_dash_table() -> html.Table:
    # Get data ordered by country
    groups = _get_tinderlike_data('country')
    # Add quote to groups
    for group_name in groups.keys():
        groups[group_name]['quote'] = '{0:.2f}%'.format(groups[group_name]['matches'] / groups[group_name]['likes'] * 100)
    # Create Table
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in ['country', 'likes', 'matches', 'quote']])] +

        # Body
        [html.Tr(
            [html.Td(i)] + [html.Td(groups[i][col]) for col in ['likes', 'matches', 'quote']]
        ) for i in groups.keys()]
    )


def _create_graph_data(group_by='country'):
    # Create graph data
    counter = _get_tinderlike_data(group_by)
    data = [
        {
            'type': 'bar',
            'name': 'Likes',
            'x': [x for x in counter.keys()],
            'y': [counter[y]['likes'] for y in counter]
        },
        {
            'type': 'bar',
            'name': 'Matches',
            'x': [x for x in counter.keys()],
            'y': [counter[y]['matches'] for y in counter]
        },
    ]
    return data


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
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
    _generate_dash_table()
])


@app.callback(
    dash.dependencies.Output('tinder-counter', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value')]
)
def _update_graph_data(value):
    return {'data': _create_graph_data(value)}


def run_dash_server():
    app.run_server(debug=True)
