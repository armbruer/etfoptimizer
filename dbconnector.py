
from sqlalchemy import Column, Integer, String, Date, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings
Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("SQL_URI"))


def create_table(engine):
    Base.metadata.create_all(engine)


class JustetfItem(Base):
    __tablename__ = 'etfs'

    # name,isin,wkn
    isin = Column(String, primary_key=True)
    name = Column(String)
    wkn = Column(String)

    # risk
    fund_size = Column(Integer)
    replication = Column(String)
    legal_structure = Column(String)
    strategy_risk = Column(String)
    fund_currency = Column(String)
    currency_risk = Column(String)
    volatility_one_year = Column(String)
    inception = Column(Date)
    # fees
    ter = Column(Float)
    # dividend/taxes
    distribution_policy = Column(String)
    distribution_frequency = Column(String)
    fund_domicile = Column(String)
    tax_data = Column(String)

    # legal structure
    fund_structure = Column(String)
    ucits_compliance = Column(String)
    fund_provider = Column(String)
    administrator = Column(String)
    investment_advisor = Column(String)
    custodian_bank = Column(String)
    revision_company = Column(String)
    fiscal_year_end = Column(Date)
    swiss_representative = Column(String)
    swiss_paying_agent = Column(String)

    # tax status
    switzerland = Column(String)
    austria = Column(String)
    uk = Column(String)

    # replica,swap,securities lending
    indextype = Column(String)
    swap_counterparty = Column(String)
    collateral_manager = Column(String)
    securities_lending = Column(String)
    securities_lending_counterparty = Column(String)
