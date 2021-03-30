
from sqlalchemy import Column, Integer, String, Date, Float, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import relationship

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("SQL_URI"))


def create_table(engine):
    """
    Creates the tables if they do not exist.
    """
    Base.metadata.create_all(engine)


def drop_static_tables(engine):
    """
    Drops all tables with static data.
    """
    Base.metadata.drop_all(bind=engine, tables=[Etf.__table__, IsinCategory.__table__, EtfCategory.__table__])


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

    #other
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
    ucits_compliance = Column(String)
    fund_provider = Column(String)
    administrator = Column(String)
    investment_advisor = Column(String)
    custodian_bank = Column(String)
    revision_company = Column(String)
    fiscal_year_end = Column(String)
    swiss_representative = Column(String)
    swiss_paying_agent = Column(String)

    # tax status
    tax_switzerland = Column(String)
    tax_austria = Column(String)
    tax_uk = Column(String)

    # replica,swap,securities lending
    indextype = Column(String)
    swap_counterparty = Column(String)
    collateral_manager = Column(String)
    securities_lending = Column(String)
    securities_lending_counterparty = Column(String)

    categories = relationship('EtfCategory', secondary='isin_category')


class IsinCategory(Base):
    """
    Describes the columns of the table matching ISINs with categories.
    """
    __tablename__ = 'isin_category'

    etf_isin = Column(String, ForeignKey('etf.isin'), primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)


class EtfCategory(Base):
    """
    Describes the columns of the categories table.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String)

    etfs = relationship('Etf', secondary='isin_category')
