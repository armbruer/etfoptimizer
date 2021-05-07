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
from db.models import EtfCategory, Etf
from db.table_manager import create_table
from optimizer import PortfolioOptimizer

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


def create_data_table(table_id, table_data, width, display):
    table = html.Div([
        dash_table.DataTable(
            id=table_id + ' Table',
            columns=table_data,
            sort_action="native"
        )
    ],
        id=table_id + ' Table Div',
        style={'width': width, 'display': display, 'padding': 10})

    return table


def create_pie_chart(pie_chart_id, names, width, display):
    pie_chart = html.Div([
        dcc.Graph(
            id=pie_chart_id + " Pie Chart",
            figure=px.pie(
                names=names,
                values=[],
            )
        )
    ],
        id=pie_chart_id + " Pie Chart Div",
        style={'width': width, 'display': display, 'padding': 10})

    return pie_chart


def create_perf_row(id, text, tooltiptext, value):
    return html.Div([
        html.Div(
            text,
            id="pp_" + id,
            style={'flex': '50%', "font-weight": "bold"},
        ),
        dbc.Tooltip(
            tooltiptext,
            target="pp_" + id,
            placement="left"
        ),
        html.Div([
            value
        ],
            id="pp_" + id + "_value",
            style={'flex': '50%'})
    ], style={"display": "flex"})


def create_performance_info():
    return html.Center(html.Div([
        html.H3('Portfolio Performance', style={"text-align": "left"}),
        create_perf_row("er", "Expected annual return:", "Das ist ein Test Text", ""),
        create_perf_row("vol", "Annual volatility:", "", ""),
        create_perf_row("ms", "Sharpe Ratio:", "", ""),
    ],
        id="pp_info",
        style={'width': '33.33%', 'display': 'block', 'padding': 10}))


def create_app(app):
    test_data_methods = [('1', 'Methode 1'), ('2', 'Methode 2'), ('3', 'Methode 3')]
    opt_res_table = [{'id': 't_asset_name', 'name': 'Name'},
                     {'id': 't_asset_weight', 'name': 'ISIN'},
                     {'id': 't_asset_weight', 'name': 'Weight'},
                     {'id': 't_asset_quantity', 'name': 'Quantity'}]

    categories = extract_categories(category_types)

    category_divs = []
    for category_type in category_types:
        category_divs.append(
            create_dropdown(((category_type.replace(' ', '')).lower()).capitalize(), categories[category_type], '20%',
                            True))

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
    output_divs.append(create_performance_info())
    output_divs.append(html.Center(create_data_table('Optimization', opt_res_table, '100%', 'none')))
    output_divs.append(html.Center(create_pie_chart('Optimization', [], '33.33%', 'none')))

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
    [Output('pp_info', 'style'),
     Output('pp_er_value', 'children'),
     Output('pp_vol_value', 'children'),
     Output('pp_ms_value', 'children'),
     Output('Optimization Table', 'data'),
     Output('Optimization Pie Chart', 'figure')],
    [Input('Optimize Button', 'n_clicks')],
    state=[State(((cat_type.replace(' ', '')).lower()).capitalize() + ' Dropdown', 'value') for cat_type in
           category_types] +
          [State('Methode Dropdown', 'value'),
           State('Investment Input Field', 'value')],
    prevent_initial_call=True
)
def update_output(num_clicks, assetklasse, anlageart, region, land, währung, sektor, rohstoffklasse, strategie,
                 laufzeit, rating, methode, betrag):
    # TODO: Integrate optimization

    isins = get_isins_from_filters()
    now = datetime.datetime.now()
    three_years_ago = now - relativedelta(months=36)

    session = Session()  # TODO get rid of this later, when we know how many threads are working in parallel in dash?
    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)
    opt = PortfolioOptimizer(isins, now, three_years_ago, session)
    session.close()
    ef = opt.efficient_frontier()
    perf_values = ef.portfolio_performance()
    weights = ef.clean_weights(rounding=3)
    etf_weights = pd.DataFrame.from_records(list(weights), columns=['isin', 'weight'])

    res = pd.concat([etf_names, etf_weights], axis=1, join="inner")

    # TODO asset quantity
    # show allocation results as pie chart
    pp = px.pie(res, values='weight', names='name', hover_name='name', hover_data=['isin'],
                title='Portfolio Allocation')
    pp.show()

    # show allocation results as data table
    res.rename(columns={"isin": "t_asset_isin", "weight": "t_asset_weight", "name": "t_asset_name"})
    dt_data = res.to_dict('records')

    # show efficient frontier
    # TODO include efficient frontier
    # fig = plot_efficient_frontier(ef, show_assets=True)

    # show performance info
    show_perf_info = {'display': 'inline-block'}
    return [show_perf_info, *perf_values, dt_data, pp]


def get_isins_from_filters() -> List[str]:
    pass  # TODO Ruben


@app.callback(
    [Output('Optimization Table Div', 'style'), Output('Optimization Pie Chart Div', 'style')],
    [Input('Ansicht Dropdown', 'value')],
    prevent_initial_call=True
)
def choose_output(value):
    if value == 'table':
        return [{'width': '100%', 'display': 'inline-block', 'padding': 10},
                {'width': '33.33%', 'display': 'none', 'padding': 10}]
    else:
        return [{'width': '100%', 'display': 'none', 'padding': 10}, {'width': '33.33%', 'display': 'inline-block', 'padding': 10}]


if __name__ == '__main__':
    create_table(sql_engine)
    create_app(app)
    app.run_server(debug=True)
