from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

from ETFOptimizer.items import EtfItem

Base = declarative_base()


class StaticETFs(Base):
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
    inception = Column(String)
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
    switzerland = Column(String)
    austria = Column(String)
    uk = Column(String)

    # replica,swap,securities lending
    indextype = Column(String)
    swap_counterparty = Column(String)
    collateral_manager = Column(String)
    securities_lending = Column(String)
    securities_lending_counterparty = Column(String)

    @staticmethod
    def fromItem(i: EtfItem):
        e = StaticETFs()
        e.name = i['name']
        e.isin = i['isin']
        e.wkn = i['wkn']

        e.fund_size = i['fund_size']
        e.replication = i['replication']
        e.legal_structure = i['legal_structure']
        e.strategy_risk = i['strategy_risk']
        e.fund_currency = i['fund_currency']
        e.volatility_one_year = i['volatility_one_year']
        e.inception = i['inception']

        e.ter = i['ter']
        e.distribution_policy = i['distribution_policy']
        e.distribution_frequency = i['distribution_frequency']
        e.fund_domicile = i['fund_domicile']
        e.tax_data = i['tax_data']

        e.fund_structure = i['fund_structure']
        e.ucits_compliance = i['ucits_compliance']
        e.fund_provider = i['fund_provider']
        e.administrator = i['administrator']
        e.investment_advisor = i['investment_advisor']
        e.custodian_bank = i['custodian_bank']
        e.revision_company = i['revision_company']
        e.fiscal_year_end = i['fiscal_year_end']
        e.swiss_representative = i['swiss_representative']
        e.swiss_paying_agent = i['swiss_paying_agent']

        e.switzerland = i['switzerland']
        e.austria = i['austria']
        e.uk = i['uk']

        e.indextype = i['indextype']
        e.swap_counterparty = i['swap_counterparty']
        e.collateral_manager = i['collateral_manager']
        e.securities_lending = i['securities_lending']
        e.securities_lending_counterparty = i['securities_lending_counterparty']
