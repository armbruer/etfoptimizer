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
from optimizer import PortfolioOptimizer, Optimizer

app = dash.Dash(__name__)
category_types = ['Asset Klasse', 'Anlageart', 'Region', 'Land', 'Währung', 'Sektor', 'Rohstoffklasse', 'Strategie',
                  'Laufzeit', 'Rating']


def extract_isin_tuples():
    """
    Extracts ISINs from the database

    This is used for the additional ISINs dropdown
    """
    session = Session()
    isins_db = session.query(IsinCategory)

    isins = []
    for isin in isins_db:
        if not (isin.etf_isin, isin.etf_isin) in isins:
            isins.append((isin.etf_isin, isin.etf_isin))

    return isins


def extract_categories(category_types):
    """
    Extracts categories from the database

    This is used for the category dropdowns
    """
    session = Session()
    categories = session.query(EtfCategory)
    session.close()

    extracted_categories = dict()
    for category_type in category_types:
        extracted_categories[category_type] = []

    for category in categories:
        extracted_categories[category.type].append((category.id, category.name))

    return extracted_categories


def create_dropdown(dropdown_id, dropdown_data, width, dropdown_multiple, default_value=None):
    """
    Create a dropdown used for category/ISIN filtering.
    """

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
            value=default_value,
        ),
    ],
        id=dropdown_id + ' Dropdown Div',
        style={'width': width, 'display': 'inline-block',
               'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25, 'padding-right': 25}, )

    return dropdown


def create_dropdown_tool_tip(dropdown_id, dropdown_data, tool_tip, width, dropdown_multiple):
    """
    Create a dropdown with a tooltip used for category/ISIN filtering.
    """

    dropdown = html.Div([
        html.Label(dropdown_id + ':', style={'padding-right': 5}),
        html.Abbr("\u003F", title=tool_tip),
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


def create_input_field(input_id, input_data, tool_tip, width, input_type, config_key):
    """
    Creates an input field with a tooltip
    """
    input_field = html.Div([
        html.Label(input_data + ':', style={'padding-right': 5}),
        html.Abbr("\u003F", title=tool_tip),
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
    """
    Creates a button with the given text
    """
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
            id='pp_' + perf_row_id + '_value', )
    ])

    return perf_row


def create_performance_info():
    """
    Creates a view that shows the performance metrics of etfs in a vertical layout
    """
    performance_info = html.Div([
        html.H3('Portfolio Performance'),
        html.Div([
            create_perf_row("er", "", "Erwartete jährliche Rendite: "),
            create_perf_row("vol", "", "Jährliche Volatilität: "),
            create_perf_row("ms", "", "Sharpe Ratio: "),
            create_perf_row("ir", "", "Investitionsrestbetrag (€): ")
        ], style={'padding-top': 20, 'padding-bottom': 20, 'padding-left': 25, 'padding-right': 25}),
    ],
        id="pp_info",
        style={'width': '100%', 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 50})

    return performance_info


def create_data_table(table_id, table_data, width):
    """
    Creates a table for displaying the portfolio allocations
    """
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
    """
    Creates a navigation bar without navigation options just for optical purposes
    """
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
    """
    Creates a figure
    """
    graph = html.Center(html.Div([
        dcc.Graph(
            id=figure_id + "_figure"
        )
    ],
        style={'width': width, 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%",
               'margin-left': "1%", 'margin-right': "1%"}))

    return graph


def create_tabs():
    """
    Creates several tabs used for displaying the optimizers results
    """
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
    """
    Combines the elements into the user interface
    """
    optimizer_methods = [('Mittelwert/Varianz', 'Mittelwert/Varianz'),
                         ('CAPM/Semikovarianz', 'CAPM/Semikovarianz'),
                         ('Exponentieller Mittelwert/Varianz', 'Exponentieller Mittelwert/Varianz')]

    categories = extract_categories(category_types)

    category_divs = []
    for category_type in category_types:
        category_divs.append(
            create_dropdown(((category_type.replace(' ', '')).lower()).capitalize(), categories[category_type], '50%',
                            True))
    isin_tuples = extract_isin_tuples()
    category_divs.append(create_dropdown_tool_tip('Zusätzliche ISINs', isin_tuples, (
        'ISINs welche zusätzlich und unabhängig von den ausgewählten Kategorien verwendet werden sollen.\n'
        'Wurden keine anderen Kategorien ausgewählt, so werden ausschließlich diese ISINs verwendet.'), '50%', True))

    optimization_divs_dropdown = []
    optimization_divs_dropdown.append(create_dropdown('Methode', optimizer_methods, '40%', False, 'Mittelwert/Varianz'))

    optimization_divs_input = []
    optimization_divs_input.append(
        create_input_field('Betrag', 'Investitionsbetrag (€)',
                           'Der Gesamtbetrag in Euro der in einem Portfolio optimal angelegt werden soll.', '20%',
                           'text', 'total_portfolio_value'))
    optimization_divs_input.append(
        create_input_field('Risikofreier Zinssatz', 'Risikofreier Zinssatz', 'Rendite einer Anlage ohne Risiko.', '20%',
                           'text', 'risk_free_rate'))
    optimization_divs_input.append(
        create_input_field('Cutoff', 'Cutoff',
                           'Werte die kleiner als Cutoff sind werden in der Portfolio Allokation nicht berücksichtigt (werden auf 0 gesetzt)',
                           '20%', 'text', 'cutoff'))

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
            html.Div(
                [dcc.Checklist(
                    id='Historic Performance Checklist',
                    options=[{'label': ' Historische Performance berechnen ', 'value': 'CHP'}],
                    value=[],
                    style={'display': 'inline', 'padding-right': 5}
                ),
                    html.Abbr("\u003F", title='Bestimmt ob historische Performance berechnet werden soll.\n'
                                              'Bei vielen ETFs wird sich die Laufzeit spürbar verschlechtern.'),
                ],
                style={'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
                       'padding-right': 25}
            ),
            create_button('Optimize', 'Optimiere'),
            html.Div(dbc.Alert(id='opt_error', is_open=False, fade=True, color='danger'),
                     style={'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10, 'padding-left': 25,
                            'padding-right': 25})],
            style=inner_style
        ),
        html.Div(
            html.Div(
                html.Div(
                    output_divs, style=inner_style
                ),
                style={'background-color': '#f8f9fa'},
            ),
            style={'display': 'none'},
            id='show_output',
        )
    ],
        style={'width': '100%', 'display': 'inline-block'},
        className="dash-bootstrap")


def get_isins_from_filters(categories: List[int], extra_isins: List[str], session) -> List[str]:
    """
    Get the ISINs for which the chosen filters apply
    """
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
    [Output('show_output', 'style'),
     Output('pp_er_value', 'children'),
     Output('pp_vol_value', 'children'),
     Output('pp_ms_value', 'children'),
     Output('pp_ir_value', 'children'),
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
           State('Cutoff Input Field', 'value'),
           State('Historic Performance Checklist', 'value')],
    prevent_initial_call=True
)
def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie,
                  laufzeit, rating, extra_isins, methode, betrag, zinssatz, cutoff, create_hist_perf):
    """
    Responsible for updating the UI when "Optimieren" button is pressed.

    Takes all category/ISIN dropdowns and input fields as parameters and updates a various fields with error messages or
    contents showing the results of the optimization in a visual and data-centric way.
    """

    show_error = [{'display': 'none'}, '', '', '', '', None, {}, {}, {}, '', True]

    # 0. Step: Check if inputs are valid
    if not betrag or not zinssatz or not cutoff:
        show_error[-2] = 'Bitte alle Eingabefelder setzen (Investitionsbetrag, Cutoff, Zinssatz)'
        return show_error

    try:
        betrag = int(betrag)
        cutoff = float(cutoff)
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
    three_years_ago = now - relativedelta(years=3)
    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)
    opt_method = Optimizer.from_str(methode)
    opt = PortfolioOptimizer(isins, three_years_ago, now, session, opt_method)

    if opt.prices.empty:
        show_error[-2] = 'Die Datenbank scheint keine Preisdaten für die ausgewählten ISINs zu enthalten :('
        session.close()
        return show_error

    opt.optimize()

    # 3. Step: Plot efficient frontier before calculating max sharpe
    # (see https://github.com/robertmartin8/PyPortfolioOpt/issues/332)
    ef_figure = plot_efficient_frontier(opt.ef, show_assets=True)

    # 4. Step: Prepare resulting values and bring them into a usable data format
    leftover, res = get_alloc_result(betrag, cutoff, etf_names, opt, zinssatz)

    # 5. Step: Show allocation results via different visuals
    pp = fill_allocation_pie(res)
    hist_figure = display_hist_perf(create_hist_perf, opt_method, isins, betrag, cutoff, zinssatz, etf_names,
                                    three_years_ago, now,
                                    session)
    dt_data = fill_datatable_allocation(res)
    session.close()

    perf_values = map(str, opt.ef.portfolio_performance())
    return [{'display': 'inline'}, *perf_values, str(leftover), dt_data, pp, ef_figure, hist_figure, '', False]


def get_alloc_result(betrag, cutoff, etf_names, opt, zinssatz):
    """
    Returns the allocation result for the optimization and performs data formatting
    """

    max_sharpe = opt.ef.max_sharpe(risk_free_rate=zinssatz)

    weights = [(k, v) for k, v in opt.ef.clean_weights(cutoff=cutoff, rounding=3).items()]
    etf_weights = pd.DataFrame.from_records(weights, columns=['isin', 'weight'])

    res = etf_names.set_index('isin').join(etf_weights.set_index('isin'))
    alloc, leftover = opt.allocated_portfolio(betrag, max_sharpe)
    alloc = [(k, v) for k, v in alloc.items()]
    etf_quantities = pd.DataFrame.from_records(alloc, columns=['isin', 'quantity'])
    res = res.join(etf_quantities.set_index('isin'))
    res = res.reset_index()
    return leftover, res


def display_hist_perf(create_hist_perf, opt_method, isins, betrag, cutoff, zinssatz, etf_names, three_years_ago, now,
                      session):
    """
    Depending on create_hist_perf the history figure is displayed or not
    """
    if create_hist_perf:
        try:
            hist_figure = fill_hist_figure(opt_method, isins, betrag, three_years_ago, now, etf_names, zinssatz, cutoff,
                                           session)
        except:
            hist_figure = show_empty_hist_figure(now, three_years_ago)
            hist_figure.add_annotation(text='Nicht genügend Daten für historische Performance.', xref='paper',
                                       yref='paper', x=0.5, y=0.5, showarrow=False)
    else:
        hist_figure = show_empty_hist_figure(now, three_years_ago)
    return hist_figure


def show_empty_hist_figure(now, three_years_ago):
    """
    Shows an empty history figure
    """
    placeholder_list = [[three_years_ago, 0], [now, 0]]
    placeholder_df = pd.DataFrame(placeholder_list, columns=['Datum', 'Wert'])
    hist_figure = px.line(placeholder_df, x=placeholder_df['Datum'], y=placeholder_df['Wert'])
    hist_figure.update_layout(yaxis_range=[0, 1])
    return hist_figure


def fill_allocation_pie(res):
    """
    Fills the pie chart with the portfolio allocation data
    """
    renamed_res = res.rename(columns={"weight": "Gewicht", "name": "Name", "isin": "ISIN"})
    pp = px.pie(renamed_res, values='Gewicht', names='Name', hover_name='Name', hover_data=['ISIN'],
                title='Portfolio Allokation')
    return pp


def fill_datatable_allocation(res):
    """
    Fills the datatable figure with the portfolio allocation data
    """

    res['weight'] = res['weight'].map("{:.3%}".format)
    res = res.rename(columns={"isin": "t_asset_isin", "weight": "t_asset_weight", "name": "t_asset_name",
                              "quantity": "t_asset_quantity"})
    dt_data = res.to_dict('records')
    return dt_data


def fill_hist_figure(opt_method, isins, betrag, three_years_ago, now, etf_names, zinssatz, cutoff, session):
    """
    Fills the history figure with data

    This figure shows what would have happened if you invested into this portfolio
    during the last three years using the data from 4-6 years ago.
    """
    six_years_ago = now - relativedelta(years=6)
    opt_hist = PortfolioOptimizer(isins, six_years_ago, three_years_ago, session, opt_method)
    opt_hist.optimize()

    _, res = get_alloc_result(betrag, cutoff, etf_names, opt_hist, zinssatz)
    relevant_isin_weights, relevant_isins = get_relevant_isins(res)
    prices = get_prices(relevant_isins, session, three_years_ago, now)

    # Consider the weights of the optimal strategy
    money_distribution = {}
    for isin in relevant_isins:
        money_distribution[isin] = (betrag * relevant_isin_weights[isin]) / prices[prices['isin'] == isin].iloc[0][
            'price']

    # Consider the invested amount
    for isin in relevant_isins:
        prices['price'] = np.where(prices['isin'] == isin,
                                   prices['price'] * money_distribution[isin],
                                   prices['price'])

    # Calculate the value of the investment
    days_all_available = min(prices['isin'].value_counts())
    prices = prices.drop(columns='isin')
    prices = prices.groupby('datapoint_date', as_index=False)['price'].sum()
    prices = prices.iloc[prices.shape[0] - days_all_available:, :]

    # Show the result
    prices = prices.rename(columns={"price": "Wert", "datapoint_date": "Datum"})
    hist_figure = px.line(prices, x=prices['Datum'], y=prices['Wert'])
    return hist_figure


def get_prices(isins, session, start_date, end_date):
    """
    Returns the prices for a date range and a list of isins
    """

    query = session.query(EtfHistory.datapoint_date, EtfHistory.isin, EtfHistory.price) \
        .filter(EtfHistory.datapoint_date.between(start_date, end_date)) \
        .filter(EtfHistory.isin.in_(isins)).statement
    prices = pd.read_sql(query, session.bind)
    return prices


def get_relevant_isins(res):
    """
    Returns only the ISINs with weight > 0 and their respective weights.
    """
    relevant_isins = []
    relevant_isin_weights = {}
    for _, row in res.iterrows():
        if row['weight'] > 0:
            relevant_isins.append(row['isin'])
            relevant_isin_weights[row['isin']] = row['weight']

    return relevant_isin_weights, relevant_isins


def flatten_categories(cats_list):
    """
    Flattens a two-dimensional list of categories into a one-dimensional list
    """
    flattened_cats = []
    for cats in cats_list:
        if cats:
            flattened_cats.append(*cats)
    return flattened_cats


def run_gui(debug=False):
    """
    Starts the GUI.
    """
    create_table(sql_engine)
    create_app(app)
    app.title = "ETF Portfolio Optimizer"
    app.run_server(debug=debug)


if __name__ == '__main__':
    run_gui(debug=True)
