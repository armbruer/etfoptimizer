from sqlalchemy import String, Date, Integer, Float, Boolean, ForeignKey, Column

from db.table_manager import Base


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

    net_assets_currency = Column(String)
    is_accumulating = Column(Boolean)
    is_derivative_based = Column(Boolean)
    is_distributing = Column(Boolean)
    is_etc = Column(Boolean)
    is_etf = Column(Boolean)
    is_hedged = Column(Boolean)
    hedged_currency = Column(String)
    is_index_fund = Column(Boolean)
    is_leveraged = Column(Boolean)
    is_physical_full = Column(Boolean)
    is_short = Column(Boolean)
    is_socially_responsible_fund = Column(Boolean)
    is_structured = Column(Boolean)
    is_swap_based_etf = Column(Boolean)
    is_synthetic_replication = Column(Boolean)


class EtfCategory(Base):
    """
    Describes ETF categories.
    """
    __tablename__ = 'category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    type = Column(String)


class IsinCategory(Base):
    __tablename__ = 'isin_category'

    etf_isin = Column(String, ForeignKey('etf.isin'), primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)


class EtfHistory(Base):
    __tablename__ = 'etf_history'

    isin = Column(String, primary_key=True)
    datapoint_date = Column(Date, primary_key=True)

    price = Column(Float)
    price_index = Column(Float)
    return_index = Column(Float)
