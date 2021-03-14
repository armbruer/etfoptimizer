# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose
from scrapy import Field
from datetime import datetime


def strip_number(x: str):
    for s in x.split('\n\t %'):
        if s.isdigit():
            return int(s)
        elif s.isdecimal():
            # convert percentage
            return float(s)/100


def string_to_date(x: str):
    # converts dates of format 01 January 1999
    return datetime.strptime(x, '%d %B %Y')


def string_to_day(x: str):
    # converts dates of format 01 January
    return datetime.strptime(x, '%d %B')


class EtfItem(scrapy.Item):
    # name,isin,wkn
    name = Field()
    isin = Field()
    wkn = Field()

    # risk
    fund_size = Field(
        input_processor=MapCompose(strip_number)
    )
    replication = Field()
    legal_structure = Field()
    strategy_risk = Field()
    fund_currency = Field()
    currency_risk = Field()
    volatility_one_year = Field(
        input_processors=MapCompose(strip_number)
    )
    inception = Field(
        input_processors=MapCompose(string_to_date)
    )
    # fees
    ter = Field(
        input_processors=MapCompose(strip_number)
    )
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
    fiscal_year_end = Field(
        input_processors=MapCompose(string_to_day)
    )
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

