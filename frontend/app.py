import datetime
from typing import List

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta

from db import Session, sql_engine
from db.models import Etf, EtfCategory, IsinCategory
from db.table_manager import create_table
from frontend.plotting import plot_efficient_frontier
from optimizer import PortfolioOptimizer

# TODO threads in dash? can we avoid multiple sessions?

app = dash.Dash("ETF Optimizer", external_stylesheets=[dbc.themes.FLATLY])
category_types = ['Asset Klasse', 'Anlageart', 'Region', 'Land', 'Währung', 'Sektor', 'Rohstoffklasse', 'Strategie',
                  'Laufzeit', 'Rating']


def extract_isin_tuples() -> List[str]:
    session = Session()
    isins_db = session.query(IsinCategory)

    isins = []
    for isin in isins_db:
        if not (isin.etf_isin, isin.etf_isin) in isins:
            isins.append((isin.etf_isin, isin.etf_isin))

    return isins


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
            options=[{'value': data_id, 'label': data_name} for data_id, data_name in
                     sorted(dropdown_data, key=lambda x: x[1])],
            placeholder=dropdown_id,
            searchable=True,
            clearable=True,
            multi=dropdown_multiple,
        ),
    ],
        id=dropdown_id + ' Dropdown Div',
        style={'width': width, 'display': 'inline-block',
               'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25, 'padding-right': 25}, )

    return dropdown


def create_input_field(input_id, input_data, width, input_type, min=None, max=None, step=None):
    input_field = html.Div([
        html.Label(input_data + ':'),
        dbc.Input(
            id=input_id + ' Input Field',
            placeholder=input_data,
            type=input_type,
            min=min,
            max=max,
            step=None,
        ),
    ],
        id=input_id + ' Input Field Div',
        style={'width': width, 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
               'padding-right': 25})

    return input_field


def create_button(button_id):
    button = html.Div([
        dbc.Button(
            button_id,
            id=button_id + ' Button',
            color='primary',
            n_clicks=0)
    ],
        id=button_id + ' Button Div',
        style={'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
               'padding-right': 25})

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
    performance_info = html.Div([
        html.H3('Portfolio Performance'),
        html.Div([
            create_perf_row("er", "", "Erwartete jährliche Rendite: "),
            create_perf_row("vol", "", "Jährliche Volatilität: "),
            create_perf_row("ms", "", "Sharpe Ratio: "),
        ], style={'padding-top': 20, 'padding-bottom': 20}),
    ],
        id="pp_info",
        style={'width': '100%', 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 50})

    return performance_info


def create_data_table(table_id, table_data, width):
    table = html.Center(html.Div([
        dash_table.DataTable(
            id=table_id + '_table',
            columns=table_data,
            sort_action="native"
        )
    ],
        style={'width': width, 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%",
               'margin-left': "1%", 'margin-right': "1%"}))

    return table


def create_navbar():
    navbar = dbc.NavbarSimple(
        brand="ETF Portfolio Optimizer",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
        sticky='top',
    )

    return navbar


def create_figure(figure_id, width):
    graph = html.Center(html.Div([
        dcc.Graph(
            id=figure_id + "_figure"
        )
    ],
        style={'width': width, 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%",
               'margin-left': "1%", 'margin-right': "1%"}))

    return graph


def create_tabs():
    graph_data = [{'id': 't_asset_name', 'name': 'Name'}, {'id': 't_asset_isin', 'name': 'ISIN'},
                  {'id': 't_asset_weight', 'name': 'Weight'}, {'id': 't_asset_quantity', 'name': 'Quantity'}]

    tabs = html.Div([
        dbc.Tabs([
            dbc.Tab(
                label='Allokation (Tabelle)',
                children=create_data_table('all', graph_data, '98%'),
                label_style={"color": "#2c3e50"},  # primary color
            ),
            dbc.Tab(
                label='Allokation (Kreisdiagramm)',
                children=create_figure('all_pie', '98%'),
                label_style={"color": "#2c3e50"},  # primary color
            ),
            dbc.Tab(
                label='Effizienzgrenze',
                children=create_figure('ef', '98%'),
                label_style={"color": "#2c3e50"},  # primary color
            ),
            dbc.Tab(
                label='Historische Performance',
                children=create_figure('historical', '98%'),
                label_style={"color": "#2c3e50"},  # primary color
            )],
            id='View Tabs',
        )],
        style={'width': '100%', 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%"},
    )

    return tabs


def create_app(app):
    test_data_methods = [('1', 'Methode 1'), ('2', 'Methode 2'), ('3', 'Methode 3')]

    categories = extract_categories(category_types)

    category_divs = []
    for category_type in category_types:
        category_divs.append(
            create_dropdown(((category_type.replace(' ', '')).lower()).capitalize(), categories[category_type], '50%',
                            True))
    isin_tuples = extract_isin_tuples()
    category_divs.append(create_dropdown('Zusätzliche Isins', isin_tuples, '50%', True))

    optimization_divs_dropdown = []
    optimization_divs_dropdown.append(create_dropdown('Methode', test_data_methods, '40%', False))

    optimization_divs_input = []
    optimization_divs_input.append(create_input_field('Betrag', 'Investitionsbetrag (€)', '20%', 'number'))
    optimization_divs_input.append(
        create_input_field('Risikofreier Zinssatz', 'Risikofreier Zinssatz', '20%', 'number'))
    optimization_divs_input.append(create_input_field('Cutoff', 'Cutoff', '20%', 'number'))

    output_divs = []
    output_divs.append(create_performance_info())
    output_divs.append(create_tabs())

    inner_style = {'margin-top': "2.5%", 'margin-bottom': "2.5%", 'margin-left': "12.5%", 'margin-right': "12.5%",
                   'width': '75%', 'display': 'inline-block'}

    app.layout = html.Div([
        create_navbar(),
        html.Div([
            html.Div(
                [html.H3('Kategorien'), *category_divs], style=inner_style
            )],
            style={'background-color': '#f8f9fa'}
        ),

        html.Div([
            html.H3('Optimierung'),
            html.Div(optimization_divs_dropdown),
            html.Div(optimization_divs_input),
            create_button('Optimize')],
            style=inner_style
        ),
        html.Div(
            html.Div(
                output_divs, style=inner_style
            ),
            style={'background-color': '#f8f9fa'}
        ),
    ], style={'width': '100%', 'display': 'inline-block'})


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


def get_isins_from_filters(categories, extra_isins, session) -> List[str]:
    isins_db = session.query(IsinCategory)

    isins = dict()
    for isin in isins_db:
        if isin.etf_isin in isins:
            isins[isin.etf_isin].append(isin.category_id)
        else:
            isins[isin.etf_isin] = [isin.category_id]

    for category in categories:
        filter_by_category(isins, category)

    filtered_isins = list(isins.keys())

    if extra_isins is None:
        return filtered_isins

    for isin in extra_isins:
        if not isin in filtered_isins:
            filtered_isins.append(isin)

    return filtered_isins


@app.callback(
    [Output('pp_er_value', 'children'),
     Output('pp_vol_value', 'children'),
     Output('pp_ms_value', 'children'),
     Output('View Tabs', 'style'),
     Output('all_table', 'data'),
     Output('all_pie_figure', 'figure'),
     Output('ef_figure', 'figure'),
     Output('historical_figure', 'figure')],
    [Input('Optimize Button', 'n_clicks')],
    state=[State(((cat_type.replace(' ', '')).lower()).capitalize() + ' Dropdown', 'value') for cat_type in
           category_types] +
          [State('Zusätzliche Isins Dropdown', 'value'), State('Methode Dropdown', 'value'), State('Betrag Input Field', 'value'),
           State('Risikofreier Zinssatz Input Field', 'value'), State('Cutoff Input Field', 'value')],
    prevent_initial_call=True
)
def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie,
                  laufzeit, rating, extra_isins, methode, betrag, zinssatz, cutoff):
    show_nothing = [None, None, None,
                    {'width': '100%', 'display': 'none', 'margin-top': "1%", 'margin-bottom': "1%"},
                    None, None, None, None]

    # 1. Step: Retrieve matching ISINs from categories
    session = Session()
    selected_categories = [assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie, laufzeit,
                           rating]
    isins = get_isins_from_filters(selected_categories, extra_isins, session)
    if not isins:
        session.close()
        return show_nothing

    # 2. Step: Optimize the portfolio and get matching names for the ISINs used
    now = datetime.datetime.now()
    three_years_ago = now - relativedelta(months=36)
    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)
    opt = PortfolioOptimizer(isins, now, three_years_ago, session)
    session.close()
    if not opt.df:
        return show_nothing

    # 3. Step: Prepare resulting values and bring them into a usable data format
    perf_values = map(str, opt.ef.portfolio_performance())
    weights = opt.ef.clean_weights(rounding=3)
    etf_weights = pd.DataFrame.from_records(list(weights), columns=['isin', 'weight'])
    res = pd.concat([etf_names, etf_weights], axis=1, join="inner")

    alloc, leftover = opt.allocated_portfolio(betrag)  # TODO show leftover
    etf_quantities = pd.DataFrame.from_records(list(alloc), columns=['isin', 'quantity'])
    res = pd.concat([res, etf_quantities], axis=1, join="inner")

    # 4. Step: Show allocation results via different visuals
    pp = px.pie(res, values='weight', names='name', hover_name='name', hover_data=['isin'],
                title='Portfolio Allocation')
    pp.show()

    res.rename(columns={"isin": "t_asset_isin", "weight": "t_asset_weight", "name": "t_asset_name",
                        "quantity": "t_asset_quantity"})
    dt_data = res.to_dict('records')

    ef_figure = plot_efficient_frontier(opt.ef, show_assets=True)

    # TODO historical figure
    show_tabs = {'width': '100%', 'display': 'inline', 'margin-top': "1%", 'margin-bottom': "1%"},
    return [*perf_values, show_tabs, dt_data, pp, ef_figure, None]


if __name__ == '__main__':
    create_table(sql_engine)
    create_app(app)
    app.title = "Etf Portfolio Optimizer"
    app.run_server(debug=True)
