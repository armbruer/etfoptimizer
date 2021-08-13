import datetime
from typing import List

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_

import config
from db import Session, sql_engine
from db.models import Etf, EtfCategory, EtfHistory, IsinCategory
from db.table_manager import create_table
from frontend.plotting import plot_efficient_frontier
from optimizer import PortfolioOptimizer

# TODO threads in dash? can we avoid multiple sessions?

app = dash.Dash(__name__)
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
            className="dash-bootstrap",
            multi=dropdown_multiple,
        ),
    ],
        id=dropdown_id + ' Dropdown Div',
        style={'width': width, 'display': 'inline-block',
               'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25, 'padding-right': 25}, )

    return dropdown


def create_input_field(input_id, input_data, width, input_type, config_key):
    input_field = html.Div([
        html.Label(input_data + ':'),
        dbc.Input(
            id=input_id + ' Input Field',
            type=input_type,
            value=config.get_value('optimizer-defaults', config_key),
            valid=True,
        ),
    ],
        id=input_id + ' Input Field Div',
        style={'width': width, 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
               'padding-right': 25})

    return input_field


def create_button(button_id, button_text):
    button = html.Div([
        dbc.Button(
            button_text,
            id=button_id + ' Button',
            color='primary',
            n_clicks=0)
    ],
        id=button_id + ' Button Div',
        style={'display': 'block', 'padding-top': 20, 'padding-bottom': 20, 'padding-left': 25,
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
        ], style={'padding-top': 20, 'padding-bottom': 20, 'padding-left': 25, 'padding-right': 25}),
    ],
        id="pp_info",
        style={'width': '100%', 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 50})

    return performance_info


def create_data_table(table_id, table_data, width):
    table = html.Center(html.Div([
        dash_table.DataTable(
            id=table_id + '_table',
            columns=table_data,
            style_cell={'textAlign': 'left'},
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
                  {'id': 't_asset_weight', 'name': 'Gewicht (%)'}, {'id': 't_asset_quantity', 'name': 'Anzahl'}]

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
    category_divs.append(create_dropdown('Zusätzliche ISINs', isin_tuples, '50%', True))

    optimization_divs_dropdown = []
    optimization_divs_dropdown.append(create_dropdown('Methode', test_data_methods, '40%', False))

    optimization_divs_input = []
    optimization_divs_input.append(
        create_input_field('Betrag', 'Investitionsbetrag (€)', '20%', 'text', 'total_portfolio_value'))
    optimization_divs_input.append(
        create_input_field('Risikofreier Zinssatz', 'Risikofreier Zinssatz', '20%', 'text', 'risk_free_rate'))
    optimization_divs_input.append(
        create_input_field('Cutoff', 'Cutoff', '20%', 'text', 'cutoff'))

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
            create_button('Optimize', 'Optimiere'),
            html.Div(dbc.Alert(id='opt_error', is_open=False, fade=True, color='danger'),
                     style={'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
                            'padding-right': 25})],
            style=inner_style
        ),
        html.Div(
            html.Div(
                output_divs, style=inner_style
            ),
            style={'background-color': '#f8f9fa'}
        ),
    ], style={'width': '100%', 'display': 'inline-block'}, className="dash-bootstrap")


def get_isins_from_filters(categories: List[int], extra_isins: List[str], session) -> List[str]:
    conds = [IsinCategory.category_id == cat for cat in categories]
    rows = session.query(IsinCategory.etf_isin).filter(
        and_(*conds) | IsinCategory.etf_isin.in_(extra_isins)).distinct().all()
    return [isin for (isin,) in rows]  # convert list of tuples to list of atomics


@app.callback(
    [Output('Betrag Input Field', 'valid'),
     Output('Risikofreier Zinssatz Input Field', 'valid'),
     Output('Cutoff Input Field', 'valid'),
     Output('Betrag Input Field', 'invalid'),
     Output('Risikofreier Zinssatz Input Field', 'invalid'),
     Output('Cutoff Input Field', 'invalid')],
    [Input('Betrag Input Field', 'value'),
     Input('Risikofreier Zinssatz Input Field', 'value'),
     Input('Cutoff Input Field', 'value')]
)
def validate_number(betrag, zinssatz, cutoff):
    values = [betrag, zinssatz, cutoff]
    res = [None, None, None, None, None, None]
    for i in range(0, len(values)):
        if values[i]:
            try:
                if i >= 1:
                    float(values[i])
                else:
                    int(values[i])
                res[i] = True
                res[i + 3] = False
            except ValueError:
                res[i] = False
                res[i + 3] = True

    return res

@app.callback(
    [Output('pp_er_value', 'children'),
     Output('pp_vol_value', 'children'),
     Output('pp_ms_value', 'children'),
     Output('View Tabs', 'style'),
     Output('all_table', 'data'),
     Output('all_pie_figure', 'figure'),
     Output('ef_figure', 'figure'),
     Output('historical_figure', 'figure'),
     Output('opt_error', 'children'),
     Output('opt_error', 'is_open')],
    [Input('Optimize Button', 'n_clicks')],
    state=[State(((cat_type.replace(' ', '')).lower()).capitalize() + ' Dropdown', 'value') for cat_type in
           category_types] +
          [State('Zusätzliche ISINs Dropdown', 'value'),
           State('Methode Dropdown', 'value'),
           State('Betrag Input Field', 'value'),
           State('Risikofreier Zinssatz Input Field', 'value'),
           State('Cutoff Input Field', 'value')],
    prevent_initial_call=True
)
def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie,
                  laufzeit, rating, extra_isins, methode, betrag, zinssatz, cutoff):
    show_error = ['', '', '',
                  {'width': '100%', 'display': 'none', 'margin-top': "1%", 'margin-bottom': "1%"},
                  None, None, None, None, '', True]

    # 0. Step: Check if inputs are valid
    if not betrag or not zinssatz or not cutoff:
        show_error[-2] = 'Bitte alle Eingabefelder setzen (Investitionsbetrag, Cutoff, Zinssatz)'
        return show_error

    try:
        betrag = int(betrag)
        cutoff = float(cutoff)  # TODO Make use of these values
        zinssatz = float(zinssatz)
    except ValueError:
        show_error[-2] = 'Bitte verwende ein korrektes Zahlenformat in den rot markierten Feldern'
        return show_error

    # 1. Step: Retrieve matching ISINs from categories
    cats_list = [assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie, laufzeit,
                 rating]
    flattened_cats = flatten_categories(cats_list)
    extra_isins = [] if not extra_isins else extra_isins  # prevent None type
    if not extra_isins and not flattened_cats:
        show_error[-2] = 'Bitte wähle zunächst mindestens eine Kategorie aus'
        return show_error

    session = Session()
    isins = get_isins_from_filters(flattened_cats, extra_isins, session)
    if not isins:
        session.close()
        show_error[-2] = 'Die Datenbank enthält keine ETFs für den ausgewählten Filter'
        return show_error

    # 2. Step: Optimize the portfolio and get matching names for the ISINs used
    now = datetime.datetime.now()
    three_years_ago = now - relativedelta(months=36)
    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)
    opt = PortfolioOptimizer(isins, three_years_ago, now, session)
    session.close()
    if opt.df.empty:
        show_error[-2] = 'Die Datenbank scheint keine Preisdaten für die ausgewählten ISINs zu enthalten :('
        return show_error

    # 3. Step: Plot efficient frontier before calculating max sharpe (see https://github.com/robertmartin8/PyPortfolioOpt/issues/332)
    ef_figure = plot_efficient_frontier(opt.ef, show_assets=True)
    max_sharpe = opt.ef.max_sharpe()

    # 4. Step: Prepare resulting values and bring them into a usable data format
    perf_values = map(str, opt.ef.portfolio_performance())
    weights = [(k, v) for k, v in opt.ef.clean_weights(rounding=3).items()]
    etf_weights = pd.DataFrame.from_records(weights, columns=['isin', 'weight'])
    res = etf_names.set_index('isin').join(etf_weights.set_index('isin'))

    alloc, leftover = opt.allocated_portfolio(betrag, max_sharpe)  # TODO show leftover
    alloc = [(k, v) for k, v in alloc.items()]
    etf_quantities = pd.DataFrame.from_records(alloc, columns=['isin', 'quantity'])
    res = res.join(etf_quantities.set_index('isin'))
    res = res.reset_index()

    # 5. Step: Show allocation results via different visuals
    pp = px.pie(res, values='weight', names='name', hover_name='name', hover_data=['isin'],
                title='Portfolio Allocation')

    relevant_isins = []
    money_distribution = {}

    for _, row in res.iterrows():
        if row['weight'] > 0:
            relevant_isins.append(row['isin'])
            money_distribution[row['isin']] = row['weight']

    session = Session()
    query = session.query(EtfHistory.datapoint_date, EtfHistory.isin, EtfHistory.price) \
            .filter(EtfHistory.datapoint_date.between(three_years_ago, now)) \
            .filter(EtfHistory.isin.in_(relevant_isins)).statement
    prices = pd.read_sql(query, session.bind)
    session.close()

    for isin in relevant_isins:
        prices['price'] = np.where(prices['isin'] == isin,
            prices['price'] * money_distribution[isin],
            prices['price'])

    days_all_available = min(prices['isin'].value_counts())

    prices = prices.drop(columns='isin')
    prices = prices.groupby('datapoint_date', as_index=False)['price'].sum()

    prices = prices.iloc[prices.shape[0] - days_all_available: , :]

    factor = betrag / prices.iloc[0]['price']
    prices['price'] = prices['price'].apply(lambda x: x*factor)

    hist_figure = px.line(prices, x=prices.datapoint_date, y=prices.price)

    res['weight'] = res['weight'].map("{:.2%}".format)
    res = res.rename(columns={"isin": "t_asset_isin", "weight": "t_asset_weight", "name": "t_asset_name",
                              "quantity": "t_asset_quantity"})
    dt_data = res.to_dict('records')

    show_tabs = {'width': '100%', 'display': 'inline', 'margin-top': "1%", 'margin-bottom': "1%"},
    # [*perf_values, show_tabs, dt_data, pp, ef_figure, None, '', False]
    return [*perf_values, None, dt_data, pp, ef_figure, hist_figure, '', False]


def flatten_categories(cats_list):
    flattened_cats = []
    for cats in cats_list:
        if cats:
            flattened_cats.append(*cats)
    return flattened_cats


if __name__ == '__main__':
    create_table(sql_engine)
    create_app(app)
    app.title = "ETF Portfolio Optimizer"
    app.run_server(debug=True)
