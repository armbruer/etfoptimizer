# Copyright (c) 2018 Robert Andrew Martin
# Source code is taken from https://github.com/robertmartin8/PyPortfolioOpt/blob/master/pypfopt/plotting.py
# and modified to work with plotly

import copy

import numpy as np
import plotly
import plotly.graph_objects as go
from plotly.graph_objs import Figure
from pypfopt import exceptions, EfficientFrontier, CLA


def _ef_default_returns_range(ef, points):
    """
    Helper function to generate a range of returns from the GMV returns to
    the maximum (constrained) returns
    """
    ef_minvol = copy.deepcopy(ef)
    ef_maxret = copy.deepcopy(ef)

    ef_minvol.min_volatility()
    min_ret = ef_minvol.portfolio_performance()[0]
    max_ret = ef_maxret._max_return()
    return np.linspace(min_ret, max_ret - 0.0001, points)


def _plot_cla(cla, points, fig, show_assets):
    """
    Helper function to plot the efficient frontier from a CLA object
    """
    if cla.weights is None:
        cla.max_sharpe()
    optimal_ret, optimal_risk, _ = cla.portfolio_performance()

    if cla.frontier_values is None:
        cla.efficient_frontier(points=points)

    mus, sigmas, _ = cla.frontier_values

    fig.add_trace(
        go.Line(
            x=sigmas,
            y=mus,
            name='Efficient Frontier',
        )
    )

    fig.add_trace(
        go.Scatter(
            optimal_risk,
            optimal_ret,
            name='Optimal',
            mode="markers",
            marker=dict(size=50, color="red", symbol='x')  # TODO markersize in matplotlib was 100
        )
    )

    if show_assets:
        fig.add_trace(
            go.Scatter(
                np.sqrt(np.diag(cla.cov_matrix)),
                cla.expected_returns,
                name='ETFs',
                mode="markers",
                marker=dict(size=10, color="black")  # TODO markersize in matplotlib was 30
            )
        )

    return fig


def _plot_ef(ef, ef_param, ef_param_range, fig: Figure, show_assets):
    """
    Helper function to plot the efficient frontier from an EfficientFrontier object
    """
    mus, sigmas = [], []

    # Create a portfolio for each value of ef_param_range
    for param_value in ef_param_range:
        ef_i = copy.deepcopy(ef)

        try:
            if ef_param == "utility":
                ef_i.max_quadratic_utility(param_value)
            elif ef_param == "risk":
                ef_i.efficient_risk(param_value)
            elif ef_param == "return":
                ef_i.efficient_return(param_value)
            else:
                raise NotImplementedError(
                    "ef_param should be one of {'utility', 'risk', 'return'}"
                )
        except exceptions.OptimizationError:
            continue

        ret, sigma, _ = ef_i.portfolio_performance()
        mus.append(ret)
        sigmas.append(sigma)

    fig.add_trace(
        go.Line(
            x=sigmas,
            y=mus,
            name='Efficient Frontier',
        )
    )

    if show_assets:
        fig.add_trace(
            go.Scatter(
                x=np.sqrt(np.diag(ef.cov_matrix)),
                y=ef.expected_returns,
                name='ETFs',
                mode="markers",
                marker=dict(size=10, color="black")  # TODO markersize in matplotlib was 30
            )
        )
    return fig


def plot_efficient_frontier(
        opt,
        ef_param="return",
        ef_param_range=None,
        points=100,
        show_assets=True,
        **kwargs
):
    """
    Plot the efficient frontier based on either a CLA or EfficientFrontier object.
    :param opt: an instantiated optimizer object BEFORE optimising an objective
    :type opt: EfficientFrontier or CLA
    :param ef_param: [EfficientFrontier] whether to use a range over utility, risk, or return.
                     Defaults to "return".
    :type ef_param: str, one of {"utility", "risk", "return"}.
    :param ef_param_range: the range of parameter values for ef_param.
                           If None, automatically compute a range from min->max return.
    :type ef_param_range: np.array or list (recommended to use np.arange or np.linspace)
    :param points: number of points to plot, defaults to 100. This is overridden if
                   an `ef_param_range` is provided explicitly.
    :type points: int, optional
    :param show_assets: whether we should plot the asset risks/returns also, defaults to True
    :type show_assets: bool, optional
    :param filename: name of the file to save to, defaults to None (doesn't save)
    :type filename: str, optional
    :param showfig: whether to plt.show() the figure, defaults to False
    :type showfig: bool, optional
    :return: plotly.graph_objs.Figure
    :rtype: plotly.graph_objs.Figure object
    """
    fig = go.Figure()

    if isinstance(opt, CLA):
        fig = _plot_cla(opt, points, fig=fig, show_assets=show_assets)
    elif isinstance(opt, EfficientFrontier):
        if ef_param_range is None:
            ef_param_range = _ef_default_returns_range(opt, points)

        fig = _plot_ef(opt, ef_param, ef_param_range, fig=fig, show_assets=show_assets)
    else:
        raise NotImplementedError("Please pass EfficientFrontier or CLA object")

    fig.update_layout(
        xaxis_title='Volatility',
        yaxis_title='Return',
        # TODO fonts, legend title, title?
    )

    fig.show()  # TODO hover info
    return fig


def plot_simulated_portfolios(mu, S, fig, n_samples=10000):
    w = np.random.dirichlet(np.ones(len(mu)), n_samples)
    rets = w.dot(mu)
    stds = np.sqrt((w.T * (S @ w.T)).sum(axis=0))
    sharpes = rets / stds

    fig.add_trace(
        go.Scatter(
            x=stds,
            y=rets,
            # TODO c paramerter was set in matplotlib with sharpes
            # marker_colorscale=plotly.colors.sequential.Viridis,
            marker=dict(size=50, reversescale=True, color=plotly.colors.sequential.Viridis, symbol='circle-dot')
        )
    )

    return fig

