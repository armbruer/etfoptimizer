from datetime import datetime

from sqlalchemy.orm import sessionmaker

from db.table_manager import db_connect, create_table
from optimizer import PortfolioOptimizer


def test_optimize():
    engine = db_connect()
    create_table(engine)

    Session = sessionmaker(engine)
    session = Session()

    start_date = datetime.strptime('01.02.2021', '%d.%m.%Y').date()
    end_date = datetime.strptime('05.02.2021', '%d.%m.%Y').date()
    isins = ['LU0392496690', 'DE000A0D8Q23']
    po = PortfolioOptimizer(isins, start_date, end_date, session)
    ef = po.calc_efficient_frontier()
    print(ef.portfolio_performance())
    print(ef.clean_weights())
    session.close()
