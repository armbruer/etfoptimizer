from datetime import datetime

import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import yfinance as yf
from dash import dash
from dateutil.relativedelta import relativedelta

from db import Session
from db.models import Etf
from frontend.app import create_app, prepare_hist_data, get_isins_from_filters, preprocess_isin_price_data, \
    create_figure
from optimizer import ReturnRiskModel, PortfolioOptimizer


def main():
    # define parameters
    total_portfolio_value = 100000
    total_years = 7
    rounding = 5
    risk_free_rate = 0.02
    cutoff = 0.00001
    period_length_in_years = 3
    opt_methods = [ReturnRiskModel.MEAN_VARIANCE]

    # open session, get ISINs and names
    session = Session()
    isins = get_isins_from_filters([1], [], session=session)

    etf_names = pd.read_sql(session.query(Etf.isin, Etf.name).filter(Etf.isin.in_(isins)).statement, session.bind)

    eval_app = dash.Dash(__name__)
    create_app(eval_app)
    eval_app.title = "ETF Portfolio Optimizer"

    msci_world = yf.Ticker("XWD.TO")

    first_day = datetime.now() - relativedelta(years=total_years)
    last_day = datetime.now()
    msci_hist = msci_world.history(start=first_day, end=last_day)
    msci_hist = msci_hist.drop(columns=['Low', 'High', 'Volume', 'Dividends', 'Open', 'Stock Splits'])

    price_on_first_day = msci_hist['Close'].values[0]
    shares = total_portfolio_value / price_on_first_day  # do not display rest
    msci_hist['Close'] = np.where(True, msci_hist['Close'] * shares, msci_hist['Close'])
    msci_hist['Name'] = 'iShares MSCI World Index ETF'
    msci_hist.reset_index(inplace=True)
    msci_hist = msci_hist.rename(columns={"Close": "Wert", "Date" : "Datum"})
    msci_hist['Datum'] = msci_hist['Datum'].apply(lambda x: str(x).split(" ")[0])

    figures = []
    for opt_method in opt_methods:

        price_dfs = []
        for years in range(total_years, -1, -1):
            start_date = datetime.now() - relativedelta(years=years + period_length_in_years)
            end_date = start_date + relativedelta(years=period_length_in_years)
            end_date_invest = end_date + relativedelta(years=1)
            if end_date_invest > datetime.now():
                break

            preprocessed_isin = preprocess_isin_price_data(isins, session, start_date)
            opt_hist = PortfolioOptimizer(preprocessed_isin, start_date, end_date, session, opt_method)
            opt_hist.prepare_optmizer()
            prices = prepare_hist_data(etf_names, opt_hist, total_portfolio_value, cutoff, risk_free_rate, rounding, session,
                                       end_date, end_date_invest, True)
            price_dfs.append(prices)
            total_portfolio_value = price_dfs[len(price_dfs) - 1].iloc[-1][1]

        prices = pd.concat(price_dfs)
        prices['Name'] = 'Optimiertes Portfolio'

        df = pd.concat([prices, msci_hist])
        hist_figure = px.line(df, x=df['Datum'], y=df['Wert'])
        figures.append(create_figure(str(opt_method), '80%', hist_figure))

    eval_app.layout = html.Div(figures)
    eval_app.run_server()
    session.close()


if __name__ == '__main__':
    main()
