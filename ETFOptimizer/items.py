# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Field, Item
from scrapy.loader import ItemLoader
from dbconnector import JustetfItem


def strip_int(x: str):
    t = x.replace(',', '')  # to handle numbers like this 7,000
    for s in t.split():
        if s.isdigit():
            return int(s)
        elif s.isdecimal():
            # convert percentage
            return float(s)/100

    return None


def strip_float(x: str):
    t = x.replace('%', '')
    for s in t.split():
        if s.isdecimal():
            # convert percentage
            return float(s)/100

    return None


def string_to_date(x: str):
    # converts dates of format 01 January 1999
    return datetime.strptime(x, '%d %B %Y')


def string_to_day(x: str):
    # converts dates of format 01 January
    return datetime.strptime(x, '%d %B')


class EtfItemLoader(ItemLoader):

    default_output_processor = TakeFirst()
    fund_size_in = MapCompose(strip_int)
    volatility_one_year_in = MapCompose(strip_float)
    inception_in = MapCompose(string_to_date)
    ter_in = MapCompose(strip_float)
    fiscal_year_end_in=MapCompose(string_to_day)


class EtfItem(Item):
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

    def to_justetf_item(self) -> JustetfItem:
        j = JustetfItem()
        j.name = l2v(self, 'name')
        j.isin = l2v(self, 'isin')
        j.wkn = l2v(self, 'wkn')

        j.fund_size = l2v(self, 'fund_size')
        j.replication = l2v(self, 'replication')
        j.legal_structure = l2v(self, 'legal_structure')
        j.strategy_risk = l2v(self, 'strategy_risk')
        j.fund_currency = l2v(self, 'fund_currency')
        j.volatility_one_year = l2v(self, 'volatility_one_year')
        j.inception = l2v(self, 'inception')

        j.ter = l2v(self, 'ter')
        j.distribution_policy = l2v(self, 'distribution_policy')
        j.distribution_frequency = l2v(self, 'distribution_frequency')
        j.fund_domicile = l2v(self, 'fund_domicile')
        j.tax_data = l2v(self, 'tax_data')

        j.fund_structure = l2v(self, 'fund_structure')
        j.ucits_compliance = l2v(self, 'ucits_compliance')
        j.fund_provider = l2v(self, 'fund_provider')
        j.administrator = l2v(self, 'administrator')
        j.investment_advisor = l2v(self, 'investment_advisor')
        j.custodian_bank = l2v(self, 'custodian_bank')
        j.revision_company = l2v(self, 'revision_company')
        j.fiscal_year_end = l2v(self, 'fiscal_year_end')
        j.swiss_representative = l2v(self, 'swiss_representative')
        j.swiss_paying_agent = l2v(self, 'swiss_paying_agent')

        j.switzerland = l2v(self, 'switzerland')
        j.austria = l2v(self, 'austria')
        j.uk = l2v(self, 'uk')

        j.indextype = l2v(self, 'indextype')
        j.swap_counterparty = l2v(self, 'swap_counterparty')
        j.collateral_manager = l2v(self, 'collateral_manager')
        j.securities_lending = l2v(self, 'securities_lending')
        j.securities_lending_counterparty = l2v(self, 'securities_lending_counterparty')

        return j


def l2v(item: EtfItem, name: str):
    if isinstance(item[name], list):
        return None if not item[name] else item[name][0]
    else:
        return None if item[name] == '-' else item[name]
