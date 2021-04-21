import os
from datetime import datetime

import pytest
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from etf_history import get_etf_history
from optimizer import PortfolioOptimizer


@pytest.fixture()
def session():
    s = UnifiedAlchemyMagicMock()
    get_etf_history(os.path.join('../docs', 'examples'), s)
    return s


def test_optimize(session):
    start_date = datetime.strptime('01.02.2021', '%d.%m.%Y').date()
    end_date = datetime.strptime('05.02.2021', '%d.%m.%Y').date()
    isins = ['LU0392496690', 'DE000A0D8Q23']
    po = PortfolioOptimizer(isins, start_date, end_date, session)
    po.optimize()
