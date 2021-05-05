import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

from dash.dependencies import Input, Output, State
from db import Session
from db.models import EtfCategory

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
category_types = ['Asset Klasse', 'Anlageart', 'Region', 'Land', 'Währung', 
                  'Sektor', 'Rohstoffklasse', 'Strategie', 'Laufzeit', 'Rating']


def extract_categories(category_types):
    session = Session()
    categories = session.query(EtfCategory)
    session.close()

    extracted_categories = dict()
    for category_type in category_types:
        extracted_categories[category_type] = []

    for category in categories:
        extracted_categories[category.type].append((category.id, category.name))

    return extracted_categories


def create_dropdown(dropdown_id, dropdown_data, width, multiple):
    dropdown = html.Div([
        dcc.Dropdown(
            id=dropdown_id + ' Dropdown',
            options=[{'value': data_id, 'label': data_name} for data_id, data_name in
                     sorted(dropdown_data, key=lambda x: x[1])],
            multi=multiple,
            clearable=True,
            placeholder=dropdown_id,
            searchable=True
        ),
    ],
        id=dropdown_id + ' Dropdown Div',
        style={'width': width, 'display': 'inline-block', 'padding': 10})

    return dropdown


def create_input_field(input_id, input_data, width):
    input_field = html.Div([
        dbc.Input(
            id=input_id + ' Input Field',
            placeholder=input_data,
            type='text'
        ),
    ],
    id = input_id + ' Input Field Div',
    style={'width': width, 'display': 'inline-block', 'padding': 10})

    return input_field


def create_button(button_id):
    button = html.Div([
        dbc.Button(
            button_id,
            id=button_id + ' Button',
            n_clicks=0)
    ],
        id=button_id + ' Button Div',
        style={'display': 'inline-block', 'padding': 10})

    return button


def create_table(table_id, table_data, width, display):
    table = html.Div([
        dash_table.DataTable(
            id=table_id + ' Table',
            columns=table_data,
        )
    ],
    id=table_id + ' Table Div',
    style={'width': width, 'display': display, 'padding': 10})

    return table


def create_pie_chart(pie_chart_id, pie_chart_data, width, display):
    data_keys = list(pie_chart_data.keys())
    data_values = []

    for key in data_keys:
        data_values.append(pie_chart_data.get(key, 0.0))

    pie_chart = html.Div([
        dcc.Graph(
            id=pie_chart_id + " Pie Chart",
            figure=px.pie(
                names=data_keys,
                values=data_values,
            )
        )
    ],
        id=pie_chart_id + " Pie Chart Div",
        style={'width': width, 'display': display, 'padding': 10})

    return pie_chart


def create_app(app):
    test_data_methods = [('1', 'Methode 1'), ('2', 'Methode 2'), ('3', 'Methode 3')]
    test_data_table = [{'id': 'column1', 'name': 'Spalte 1'}, {'id': 'column2', 'name': 'Spalte 2'}, {'id': 'column3', 'name': 'Spalte 3'}]
    test_data_pie_chart = {'A' : 10, 'B' : 10, 'C' : 10}

    categories = extract_categories(category_types)

    category_divs = []
    for category_type in category_types:
        category_divs.append(create_dropdown(((category_type.replace(' ', '')).lower()).capitalize(), categories[category_type], '20%', True))

    method_divs = []
    method_divs.append(create_dropdown('Methode', test_data_methods, '20%', False))

    investment_divs = []
    investment_divs.append(create_input_field('Investment', 'Betrag in Euro', '20%'))

    run_optimization_divs = []
    run_optimization_divs.append(create_button('Optimize'))

    views = [('table', 'Tabelle'), ('graph', 'Graph')]

    output_switch_divs = []
    output_switch_divs.append(create_dropdown('Ansicht', views, '20%', False))

    output_divs = []
    output_divs.append(html.Center(create_table('Optimization', test_data_table, '100%', 'none')))
    output_divs.append(html.Center(create_pie_chart('Optimization', test_data_pie_chart, '33.33%', 'none')))

    app.layout = html.Div([
        html.H1('ETF Portfolio Optimizer'),
        html.Hr(),
        html.H3('Kategorien'),
        html.Div(
            category_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Hr(),
        html.H3('Optimierungsmethoden'),
        html.Div(
            method_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Hr(),
        html.H3('Investitionsbetrag'),
        html.Div(
            investment_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Div(
            run_optimization_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Hr(),
        html.H3('Optimiertes Portfolio'),
        html.Div(
            output_switch_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Div(
            output_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
    ], style={'width': '90%', 'display': 'inline-block', 'margin-top': "50px", 'margin-bottom': "50px", 'margin-left': "5%", 'margin-right': "5%"})


@app.callback(
    [Output(component_id='Optimization Table', component_property='data'), Output(component_id='Optimization Pie Chart', component_property='figure')],
    [Input(component_id='Optimize Button', component_property='n_clicks')],
    state = [State(component_id=((category_type.replace(' ', '')).lower()).capitalize() + ' Dropdown' , component_property='value') for category_type in category_types] +
    [State(component_id='Methode Dropdown', component_property='value'), State(component_id='Investment Input Field', component_property='value')],
    prevent_initial_call = True
)

def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie, laufzeit, rating, methode, betrag):
    # TODO: Integrate optimization
    figure = px.pie(
                values=[10, 10, 10, 10],
                names=['A', 'B', 'C', 'D']
            )
    return [None, figure]


@app.callback(
    [Output(component_id='Optimization Table Div', component_property='style'), Output(component_id='Optimization Pie Chart Div', component_property='style')],
    [Input(component_id='Ansicht Dropdown', component_property='value')],
    prevent_initial_call = True
)

def choose_output(value):
    if value == 'table':
        return [{'width': '100%', 'display': 'inline-block', 'padding': 10}, {'width': '33.33%', 'display': 'none', 'padding': 10}]
    else:
        return [{'width': '100%', 'display': 'none', 'padding': 10}, {'width': '33.33%', 'display': 'inline-block', 'padding': 10}]


if __name__ == '__main__':
    create_app(app)
    app.run_server(debug=True)
