# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class EtfItem(scrapy.Item):
    # name,isin,wkn
    name = Field()
    isin = Field()
    wkn = Field()

    # risk
    fund_size = Field()
    replication = Field()
    legal_structure = Field()
    strategy_risk = Field()
    fund_currency = Field()
    currency_risk = Field()
    volatility_one_year = Field()
    inception = Field()
    # fees
    ter = Field()
    # dividend/taxes
    distribution_policy = Field()
    distribution_frequency = Field()
    fund_domicile = Field()
    tax_data = Field()

    # legal structure
    fund_structure = Field()
    ucits_compliance = Field()
    fund_provider = Field()
    administrator = Field()
    investment_advisor = Field()
    custodian_bank = Field()
    revision_company = Field()
    fiscal_year_end = Field()
    swiss_representative = Field()
    swiss_paying_agent = Field()

    # tax status
    switzerland = Field()
    austria = Field()
    uk = Field()

    # replica,swap,securities lending
    indextype = Field()
    swap_counterparty = Field()
    collateral_manager = Field()
    securities_lending = Field()
    securities_lending_counterparty = Field()

