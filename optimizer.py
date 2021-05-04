from dataclasses import dataclass
from datetime import date
from typing import List

import pandas as pd
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

    def efficient_frontier(self):
        mu = mean_historical_return(self.df)
        S = CovarianceShrinkage(self.df).ledoit_wolf()
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()  # todo risk free rate
        return ef
