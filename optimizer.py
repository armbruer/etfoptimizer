from dataclasses import dataclass
from datetime import date
from typing import List

import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from sqlalchemy.orm import Session

from db.dbmodels import EtfHistory


@dataclass
class PortfolioOptimizer:
    isins: List[str]
    start_date: date
    end_date: date
    session: Session

    def __post_init__(self):
        query = self.session.query(EtfHistory.datapoint_date, EtfHistory.price) \
            .filter(EtfHistory.datapoint_date.between(self.start_date, self.end_date)) \
            .filter(EtfHistory.isin.in_(self.isins)).statement
        self.df = pd.read_sql(query, self.session.bind, index_col=['datapoint_date', 'isin'])
        self.df = self.df.unstack('isin')

    def optimize(self):
        mu = mean_historical_return(self.df)
        S = CovarianceShrinkage(self.df).ledoit_wolf()
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()  # exact results
        print(ef.clean_weights())
        ef.portfolio_performance(verbose=True)
