import logging
from dataclasses import dataclass
from datetime import date
from typing import List
from enum import Enum, unique

import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return, capm_return, ema_historical_return
from pypfopt.risk_models import CovarianceShrinkage, semicovariance
from sqlalchemy.orm import Session

from db.models import EtfHistory


@unique
class Optimizer(Enum):
    """
    Different Optimizers
    """
    MEAN_VARIANCE = 0
    CAPM_SEMICOVARIANCE = 1
    EMA_VARIANCE = 2

    @staticmethod
    def from_str(optimizer: str):
        """
        Converts from str to Optimizer
        """
        if optimizer == 'Mittelwert/Varianz':
            return Optimizer.MEAN_VARIANCE
        elif optimizer == 'CAPM/Semikovarianz':
            return Optimizer.CAPM_SEMICOVARIANCE
        elif optimizer == 'Exponentieller Mittelwert/Varianz':
            return Optimizer.EMA_VARIANCE
        else:
            raise ValueError(f"Unknown value for Optimizer enum: {optimizer}")


@dataclass
class PortfolioOptimizer:
    """
    PortfolioOptimizer is a small wrapper for retrieving the price data from database within a date range and
    pushing it into the respective optimizers.
    """
    isins: List[str]
    start_date: date
    end_date: date
    session: Session
    optimize_method: Optimizer

    def __post_init__(self):
        query = self.session.query(EtfHistory.isin, EtfHistory.datapoint_date, EtfHistory.price) \
            .filter(EtfHistory.datapoint_date.between(self.start_date, self.end_date)) \
            .filter(EtfHistory.isin.in_(self.isins)).statement
        self.prices = pd.read_sql(query, self.session.bind)
        self.prices = self.prices.pivot(index='datapoint_date', columns='isin', values='price')

        if self.prices.empty:
            logging.warning(f"Detected empty dataframe for given ISINs. Optimizing will not produce any results.")

    def optimize(self):
        """
        Calls the chosen optimizer on the given data.
        """
        if self.optimize_method is Optimizer.MEAN_VARIANCE:
            self.__mean_variance_optimizer()
            return True
        elif self.optimize_method is Optimizer.CAPM_SEMICOVARIANCE:
            self.__capm_semicovariance_optimizer()
            return True
        elif self.optimize_method is Optimizer.EMA_VARIANCE:
            self.__ema_variance_optimizer()
            return True

        return False

    def __mean_variance_optimizer(self):
        mu = mean_historical_return(self.prices)
        S = CovarianceShrinkage(self.prices).ledoit_wolf()
        self.ef = EfficientFrontier(mu, S)

    def __capm_semicovariance_optimizer(self):
        mu = capm_return(self.prices)
        S = semicovariance(self.prices)
        self.ef = EfficientFrontier(mu, S)

    def __ema_variance_optimizer(self):
        mu = ema_historical_return(self.prices)
        S = CovarianceShrinkage(self.prices).ledoit_wolf()
        self.ef = EfficientFrontier(mu, S)

    def allocated_portfolio(self, total_portfolio_value, max_sharpe):
        """
        Allocates the portfolio according to the optimization result
        """
        latest_prices = get_latest_prices(self.prices)  # TODO greedy allocation?
        da = DiscreteAllocation(max_sharpe, latest_prices, total_portfolio_value=total_portfolio_value)
        return da.lp_portfolio()
