
import sys

import click
from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, Integer, String, Date, Float, create_engine, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    global engine
    if engine is None:
        uri = get_project_settings().get("SQL_URI")
        if not uri:
            click.echo("Please setup the database connection first!")
            sys.exit(1)
        engine = create_engine(uri)
    return engine


def create_table(engine):
    """
    Creates the tables if they do not exist.
    """
    Base.metadata.create_all(engine)


def drop_static_tables(engine):
    """
    Drops all tables with static data.
    """
    Base.metadata.drop_all(bind=engine, tables=[Etf.__table__, IsinCategory.__table__])


class Etf(Base):
    """
    Describes the columns of the etf table.
    """
    __tablename__ = 'etf'

    # name,isin,wkn
    isin = Column(String, primary_key=True)
    wkn = Column(String)
    name = Column(String)

    # risk
    fund_size = Column(Integer)
    replication = Column(String)
    legal_structure = Column(String)
    strategy_risk = Column(String)
    fund_currency = Column(String)
    currency_risk = Column(String)
    volatility_one_year = Column(String)
    inception = Column(Date)

    # other
    benchmark_index = Column(String)

    # fees
    ter = Column(Float)
    # dividend/taxes
    distribution_policy = Column(String)
    distribution_frequency = Column(String)
    fund_domicile = Column(String)
    tax_data = Column(String)

    # legal structure
    fund_structure = Column(String)
    ucits_compliance = Column(Boolean)
    fund_provider = Column(String)
    administrator = Column(String)
    investment_advisor = Column(String)
    custodian_bank = Column(String)
    revision_company = Column(String)
    fiscal_year_end_month = Column(String)
    swiss_representative = Column(String)
    swiss_paying_agent = Column(String)

    # tax status
    tax_germany = Column(String)
    tax_switzerland = Column(String)
    tax_austria = Column(String)
    tax_uk = Column(String)

    # replica,swap,securities lending
    indextype = Column(String)
    swap_counterparty = Column(String)
    collateral_manager = Column(String)
    securities_lending = Column(Boolean)
    securities_lending_counterparty = Column(String)


class IsinCategory(Base):
    """
    Describes the columns of the table matching ISINs with categories.
    """
    __tablename__ = 'isin_category'

    etf_isin = Column(String, ForeignKey('etf.isin'), primary_key=True)
    category = Column(String, primary_key=True)
