import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import yfinance as yf

from datetime import datetime
from dash import dash
from dateutil.relativedelta import relativedelta
from db import Session
from db.models import Etf
from frontend.app import create_app, prepare_hist_data
from optimizer import Optimizer, PortfolioOptimizer


def create_figure(figure_id, width, figure):
    """
    Creates a figure
    """
    graph = html.Center(html.Div([
        dcc.Graph(
            id=figure_id + "_figure",
            figure=figure,
        )
    ],
        style={'width': width, 'display': 'inline-block', 'margin-top': "1%", 'margin-bottom': "1%",
               'margin-left': "1%", 'margin-right': "1%"}))

    return graph

def main():
    # define parameters
    total_portfolio_value = 1000000
    total_years = 10
    rounding = 5
    risk_free_rate = 0.02
    cutoff = 0.000001
    period_length_in_years = 3
    opt_methods = [Optimizer.MEAN_VARIANCE, Optimizer.EMA_VARIANCE, Optimizer.CAPM_SEMICOVARIANCE]

    # open session, get ISINs and names
    session = Session()
    isins = []
    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)

    eval_app = dash.Dash(__name__)
    create_app(eval_app)
    eval_app.title = "ETF Portfolio Optimizer"

    msci_world = yf.Ticker("XWD.TO")
    print(msci_world.info)

    first_day = datetime.now() - relativedelta(years=total_years)
    last_day = datetime.now()
    msci_hist = msci_world.history(start=first_day, end=last_day)
    msci_hist_prices = msci_hist[['Close']]
    msci_hist_prices.rename(columns={"Close", "Wert"})
    msci_hist_prices['Name'] = 'iShares MSCI World Index ETF'


    figures = []
    for opt_method in opt_methods:

        price_dfs = []
        for years in range(total_years, -1, -1):
            start_date = datetime.now() - relativedelta(years=years + period_length_in_years)
            end_date = start_date + relativedelta(years=period_length_in_years)
            end_date_invest = end_date + relativedelta(years=1)

            opt_hist = PortfolioOptimizer(isins, start_date, end_date, session, opt_method)
            opt_hist.optimize()
            prices = prepare_hist_data(etf_names, opt_hist, total_portfolio_value, cutoff, risk_free_rate, rounding, session,
                                       end_date, end_date_invest)
            price_dfs.append(prices)

        prices = pd.concat(price_dfs)
        prices['Name'] = 'Optimiertes Portfolio'
        hist_figure = px.line(prices, x=prices['Datum'], y=prices['Wert'])
        figures.append(create_figure(str(opt_method), '80%', hist_figure))

    eval_app.layout = html.Div(figures)
    eval_app.run_server()
    session.close()


if __name__ == '__main__':
    main()
