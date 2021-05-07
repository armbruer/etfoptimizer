
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import datetime
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from typing import List

from db import sql_engine, Session
from db.models import Etf, EtfCategory, IsinCategory
from db.table_manager import create_table
from optimizer import PortfolioOptimizer


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
category_types = ['Asset Klasse', 'Anlageart', 'Region', 'Land', 'Währung', 'Sektor', 'Rohstoffklasse', 'Strategie', 'Laufzeit', 'Rating']


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


def create_dropdown(dropdown_id, dropdown_data, width, dropdown_multiple):
    dropdown = html.Div([
        html.Label(dropdown_id + ':'),
        dcc.Dropdown(
            id=dropdown_id + ' Dropdown',
            options=[{'value': data_id, 'label': data_name} for data_id, data_name in sorted(dropdown_data, key=lambda x: x[1])],
            placeholder=dropdown_id,
            searchable=True,
            clearable=True,
            multi=dropdown_multiple,
        ),
    ],
        id=dropdown_id + ' Dropdown Div',
        style={'width': width, 'display': 'inline-block', 'padding': 10},)

    return dropdown


def create_input_field(input_id, input_data, width, input_type):
    input_field = html.Div([
        html.Label(input_data + ':'),
        dbc.Input(
            id=input_id + ' Input Field',
            placeholder=input_data,
            type=input_type
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


def create_perf_row(perf_row_id, perf_row_data, perf_row_text):
    perf_row = html.Div([
        html.Div(
            perf_row_text,
            id='pp_' + perf_row_id,
            style={'font-weight': 'bold'},
        ),
        html.Div([
            perf_row_data
        ],
            id='pp_' + perf_row_id + '_value',)
    ])
    
    return perf_row


def create_performance_info():
    performance_info = html.Center(html.Div([
        html.H3('Portfolio Performance'),
        create_perf_row("er", "", "Erwartete jährliche Rendite: "),
        create_perf_row("vol", "", "Jährliche Volatilität: "),
        create_perf_row("ms", "", "Sharpe Ratio: "),
    ],
        id="pp_info",
        style={'width': '33.33%', 'display': 'inline-block', 'padding': 10}))

    return performance_info


def create_data_table(table_id, table_data, width):
    table = html.Center(html.Div([
        dash_table.DataTable(
            id=table_id + ' Table',
            columns=table_data, 
            sort_action="native"
        )
    ],
    style={'width': '98%', 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%", 'margin-left': "1%", 'margin-right': "1%"}))

    return table


def create_graph(graph_id, graph_data, width, graph_names):
    graph = html.Center(html.Div([
        dcc.Graph(
            id=graph_id + " Graph",
            figure=px.pie(
                names=graph_names,
                values=graph_data,
            )
        )
    ],
        style={'width': '98%', 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%", 'margin-left': "1%", 'margin-right': "1%"}))

    return graph


def create_tabs():
    tabs = html.Div([
        dcc.Tabs([
            dcc.Tab(
                label='Tabelle',
                children=create_data_table('Optimization', [{'id': 't_asset_name', 'name': 'Name'}, {'id': 't_asset_isin', 'name': 'ISIN'}, 
                                                            {'id': 't_asset_weight', 'name': 'Weight'}, {'id': 't_asset_quantity', 'name': 'Quantity'}], '75%'),
            ),
            dcc.Tab(
                label='Graph',
                children=create_graph('Optimization', [], '75%', [])
            )],
            id='View Tabs'
        )],
        style={'width': '100%', 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%"},
    )
    
    return tabs


def create_app(app):
    test_data_methods = [('1', 'Methode 1'), ('2', 'Methode 2'), ('3', 'Methode 3')]

    categories = extract_categories(category_types)

    category_divs = []
    for category_type in category_types:
        category_divs.append(create_dropdown(((category_type.replace(' ', '')).lower()).capitalize(), categories[category_type], '50%', True))

    optimization_divs = []
    optimization_divs.append(create_dropdown('Methode', test_data_methods, '100%', False))
    optimization_divs.append(create_input_field('Investment', 'Betrag in Euro', '100%', 'text'))
    optimization_divs.append(create_button('Optimize'))

    output_divs = []
    output_divs.append(create_performance_info())
    output_divs.append(create_tabs())

    app.layout = html.Div([
        html.H1('ETF Portfolio Optimizer'),
        html.Hr(),
        html.H3('Kategorien'),
        html.Div(
            category_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Hr(),
        html.H3('Optimierung'),
        html.Div(
            optimization_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Hr(),
        html.Div(
            output_divs, style={'width': '100%', 'display': 'inline-block'}
        ),
    ], style={'width': '75%', 'display': 'inline-block', 'margin-top': "2.5%", 'margin-bottom': "2.5%", 'margin-left': "12.5%", 'margin-right': "12.5%"})


def filter_by_category(isins, category):
    if category is None:
        return

    isins_copy = isins.copy()
    for isin in isins_copy.keys():
        stays = False
        for selection in category:
            if selection in isins_copy[isin]:
                stays = True

        if not stays:
            isins.pop(isin)


def get_isins_from_filters(categories) -> List[str]:
    session = Session()
    isins_db = session.query(IsinCategory)
    session.close()

    isins = dict()
    for isin in isins_db:
        if isin.etf_isin in isins:
            isins[isin.etf_isin].append(isin.category_id)
        else:
            isins[isin.etf_isin] = [isin.category_id]

    for category in categories:
        filter_by_category(isins, category)

    print(isins.keys())

    return isins.keys()


@app.callback(
    [Output('pp_info', 'style'), Output('pp_er_value', 'children'), Output('pp_vol_value', 'children'),
     Output('pp_ms_value', 'children'), Output(('View Tabs'), 'children')],
    [Input('Optimize Button', 'n_clicks')],
    state=[State(((cat_type.replace(' ', '')).lower()).capitalize() + ' Dropdown', 'value') for cat_type in category_types] +
          [State('Methode Dropdown', 'value'), State('Investment Input Field', 'value')],
    prevent_initial_call=True
)
def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie, laufzeit, rating, methode, betrag):
    # TODO: integrate optimization

    selected_categories = [assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie, laufzeit, rating]
    isins = get_isins_from_filters(selected_categories)
    #now = datetime.datetime.now()
    #three_years_ago = now - relativedelta(months=36)

    #session = Session()  # TODO get rid of this later, when we know how many threads are working in parallel in dash?
    #etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)
    #opt = PortfolioOptimizer(isins, now, three_years_ago, session)
    #session.close()
    #ef = opt.efficient_frontier()
    #perf_values = ef.portfolio_performance()
    #weights = ef.clean_weights(rounding=3)
    #etf_weights = pd.DataFrame.from_records(list(weights), columns=['isin', 'weight'])

    #res = pd.concat([etf_names, etf_weights], axis=1, join="inner")

    # TODO asset quantity
    # show allocation results as pie chart
    #pp = px.pie(res, values='weight', names='name', hover_name='name', hover_data=['isin'], title='Portfolio Allocation')
    #pp.show()

    # show allocation results as data table
    #res.rename(columns={"isin": "t_asset_isin", "weight": "t_asset_weight", "name": "t_asset_name"})
    #dt_data = res.to_dict('records')

    # show efficient frontier
    # TODO include efficient frontier
    # fig = plot_efficient_frontier(ef, show_assets=True)

    # show performance info
    #show_perf_info = {'display': 'inline-block'}
    #return [show_perf_info, *perf_values, dt_data, pp]
    return[None, None, None, None, None]


if __name__ == '__main__':
    create_table(sql_engine)
    create_app(app)
    app.run_server(debug=True)
