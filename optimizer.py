import logging
from dataclasses import dataclass
from datetime import date
from enum import unique, IntEnum
from typing import List

import numpy as np
import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return, capm_return, ema_historical_return
from pypfopt.risk_models import CovarianceShrinkage, semicovariance
from sqlalchemy.orm import Session

from db.models import EtfHistory


@unique
class ReturnRiskModel(IntEnum):
    """
    Different combinations of models for the expected return and risk of a portfolio
    """
    MEAN_VARIANCE = 0
    CAPM_SEMICOVARIANCE = 1
    EMA_VARIANCE = 2


@unique
class Optimizer(IntEnum):
    """
    Different combinations of models for the expected return and risk of a portfolio
    """
    MAX_SHARPE = 0
    EFFICIENT_RETURN = 1
    EFFICIENT_RISK = 2


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
    return_risk_model: ReturnRiskModel = ReturnRiskModel.MEAN_VARIANCE

    def __post_init__(self):
        query = self.session.query(EtfHistory.isin, EtfHistory.datapoint_date, EtfHistory.price) \
            .filter(EtfHistory.datapoint_date.between(self.start_date, self.end_date)) \
            .filter(EtfHistory.isin.in_(self.isins)).statement
        self.prices = pd.read_sql(query, self.session.bind)
        self.prices = self.prices.pivot(index='datapoint_date', columns='isin', values='price')
        self.prices = self.prices.dropna()

        if self.prices.empty:
            logging.warning(f"Detected empty dataframe for given ISINs. Optimizing will not produce any results.")

    def prepare_optmizer(self):
        """
        Prepares the optimizer according to the chosen ReturnRiskModel on the retrieved data
        """
        if self.return_risk_model is ReturnRiskModel.MEAN_VARIANCE:
            mu = mean_historical_return(self.prices)
            mu = np.clip(mu, 0, 1)
            S = CovarianceShrinkage(self.prices).ledoit_wolf()
        elif self.return_risk_model is ReturnRiskModel.CAPM_SEMICOVARIANCE:
            mu = capm_return(self.prices)
            mu = np.clip(mu, 0, 1)
            S = semicovariance(self.prices)
        elif self.return_risk_model is ReturnRiskModel.EMA_VARIANCE:
            mu = ema_historical_return(self.prices)
            mu = np.clip(mu, 0, 1)
            S = CovarianceShrinkage(self.prices).ledoit_wolf()
        else:
            raise ValueError("return_risk_model must not be None")

        self.ef = EfficientFrontier(mu, S)

    def allocate_portfolio_optimize(self, total_portfolio_value, max_sharpe):
        """
        Allocates the portfolio optimally utilizing integer programming
        """
        latest_prices = get_latest_prices(self.prices)
        da = DiscreteAllocation(max_sharpe, latest_prices, total_portfolio_value=total_portfolio_value)
        return da.lp_portfolio(solver="GUROBI", reinvest=True)

    def allocated_portfolio_greedy(self, total_portfolio_value, max_sharpe):
        """
        Allocates the portfolio according to the optimization result
        """
        latest_prices = get_latest_prices(self.prices)
        da = DiscreteAllocation(max_sharpe, latest_prices, total_portfolio_value=total_portfolio_value)
        return da.greedy_portfolio(reinvest=True)
