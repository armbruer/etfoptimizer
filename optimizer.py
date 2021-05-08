import logging
from dataclasses import dataclass
from datetime import date
from typing import List

import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from sqlalchemy.orm import Session

from db.models import EtfHistory


@dataclass
class PortfolioOptimizer:
    isins: List[str]
    start_date: date
    end_date: date
    session: Session

    def __post_init__(self):
        query = self.session.query(EtfHistory.isin, EtfHistory.datapoint_date, EtfHistory.price) \
            .filter(EtfHistory.datapoint_date.between(self.start_date, self.end_date)) \
            .filter(EtfHistory.isin.in_(self.isins)).statement
        self.df = pd.read_sql(query, self.session.bind)
        self.df = self.df.pivot(index='datapoint_date', columns='isin', values='price')

        self.calc_efficient_frontier()

    def calc_efficient_frontier(self):
        if self.df.empty:
            logging.warning(f"Could not optimize as there is no data matching parameters :(")
            logging.warning("f{self}")
            return

        mu = mean_historical_return(self.df)
        S = CovarianceShrinkage(self.df).ledoit_wolf()
        self.ef = EfficientFrontier(mu, S)
        self.max_sharpe = self.ef.max_sharpe()

    def allocated_portfolio(self, total_portfolio_value):
        latest_prices = get_latest_prices(self.df)  # TODO greedy allocation?
        da = DiscreteAllocation(self.max_sharpe, latest_prices, total_portfolio_value=total_portfolio_value)
        return da.lp_portfolio()
