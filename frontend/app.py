import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

from dash.dependencies import Input, Output

# from dbconnector import db_connect, EtfCategory
# from sqlalchemy.orm import sessionmaker

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

#engine = db_connect()
#Session = sessionmaker(engine)
#session = Session()
#categories = session.query(EtfCategory).all()
#session.close()

categories = [(1, 'USA', ''), (2, 'Germany', ''), (3, 'China', '')]

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='categories-filter1',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        ),
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter2',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter3',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter4',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter5',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='categories-filter6',
            options=[{'label': cat_name, 'value': cat_id} for cat_id, cat_name, _ in categories],
            multi=True,
            clearable=True,
            placeholder='Select categories for your portfolio',
            searchable=True
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dbc.Button('Optimize', id = 'optimize-button')
    ], style={'display': 'inline-block', 'padding': 10}),
    html.Div([
        dash_table.DataTable(
            id='data-table',
            columns=[{'id': 'column1', 'name': 'Column 1'},
            {'id': 'column2', 'name': 'Column 2'},
            {'id': 'column3', 'name': 'Column 3'}],
        )
    ], style={'width': '100%', 'display': 'inline-block', 'padding': 10}),
    html.Div([
        dcc.Graph(
            id='data-graph',
            figure=px.pie(
                values=[25,25,50],
                names=['A', 'B', 'C']
            )
        )
    ], style={'width': '33.33%', 'display': 'inline-block', 'padding': 10, 'textAlign': 'center'}),
])  

@app.callback(
    Output(component_id='data-table', component_property='data'),
    [Input(component_id='optimize-button', component_property='n_clicks'),
    Input(component_id='categories-filter1',component_property='value'),
    Input(component_id='categories-filter2',component_property='value'),
    Input(component_id='categories-filter3',component_property='value'),
    Input(component_id='categories-filter4',component_property='value'),
    Input(component_id='categories-filter5',component_property='value'),
    Input(component_id='categories-filter6',component_property='value')]
)
def update_table(num_clicks, val1, val2, val3, val4, val5, val6):
    # TODO: Update table with optimized values
    return None

@app.callback(
    Output(component_id='data-graph', component_property='figure'),
    [Input(component_id='optimize-button', component_property='n_clicks'),
    Input(component_id='categories-filter1',component_property='value'),
    Input(component_id='categories-filter2',component_property='value'),
    Input(component_id='categories-filter3',component_property='value'),
    Input(component_id='categories-filter4',component_property='value'),
    Input(component_id='categories-filter5',component_property='value'),
    Input(component_id='categories-filter6',component_property='value')]
)
def update_graph(num_clicks, val1, val2, val3, val4, val5, val6):
    # TODO: Update graph with optimized values
    figure = px.pie(
                values=[10,10,10],
                names=['A', 'B', 'C']
            )
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
