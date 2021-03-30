# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Field, Item
from scrapy.loader import ItemLoader
from dbconnector import Etf
import locale


def strip_int(x: str):
    """
    Returns the first integer in a string.
    """
    t = x.replace(',', '')  # to handle numbers like 7,000

    for s in t.split():
        if s.isdigit():
            return int(s)

    return None


def strip_float(x: str):
    """
    Returns the first float in a string.
    """
    t = x.replace('%', '')
    res = None

    for s in t.split():
        try:
            # convert percentage
            res = float(s)/100
            break
        except:
            continue

    return res


def string_to_date(x: str):
    """
    Converts a string date of format 01 January 1999 into a date.
    """
    res = None
    # TODO more locale flexibility, also test on Window$
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
        res = datetime.strptime(x, '%d %B %Y')
    except ValueError:
        locale.setlocale(locale.LC_ALL, 'de_DE')
        res = datetime.strptime(x, '%d %B %Y')
    return res


def empty_to_none(x: str):
    """
    Converts '-' value to None.
    """
    return x if x.strip() != '-' else None


class EtfItemLoader(ItemLoader):
    """
    The EtfItemLoader defines processors for converting parsed values into the correct datatype and
    removing unwanted clutter from strings for etf data.
    """

    default_output_processor = TakeFirst()
    fund_size_in = MapCompose(strip_int)
    volatility_one_year_in = MapCompose(strip_float)
    inception_in = MapCompose(empty_to_none, string_to_date)
    ter_in = MapCompose(strip_float)
    fiscal_year_end_in=MapCompose(empty_to_none)
    benchmark_index_in=MapCompose(str.strip)
    isin_in = MapCompose(lambda x: x.replace(',', ''))


class EtfCategoryItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    isin_in = MapCompose(lambda x: x.replace(',', ''))


class EtfItem(Item):
    """
    EtfItem represents static data about an ETF.
    """

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

    #other
    benchmark_index = Field()

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
    tax_switzerland = Field()
    tax_austria = Field()
    tax_uk = Field()

    # replica,swap,securities lending
    indextype = Field()
    swap_counterparty = Field()
    collateral_manager = Field()
    securities_lending = Field()
    securities_lending_counterparty = Field()

    def to_etfitemdb(self) -> Etf:
        """Converts an EtfItem into a JustetfItem.
        The purpose is to convert from a scrapy representation to an sqlalchemy representation of the same item,
        so the item can be stored in a database"""

        j = Etf()
        j.name = l2v(self, 'name')
        j.isin = l2v(self, 'isin')
        j.wkn = l2v(self, 'wkn')

        j.fund_size = l2v(self, 'fund_size')
        j.replication = l2v(self, 'replication')
        j.legal_structure = l2v(self, 'legal_structure')
        j.strategy_risk = l2v(self, 'strategy_risk')
        j.fund_currency = l2v(self, 'fund_currency')
        j.currency_risk = l2v(self, 'currency_risk')
        j.volatility_one_year = l2v(self, 'volatility_one_year')
        j.inception = l2v(self, 'inception')

        j.benchmark_index = l2v(self, 'benchmark_index')

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

        j.tax_switzerland = l2v(self, 'tax_switzerland')
        j.tax_austria = l2v(self, 'tax_austria')
        j.tax_uk = l2v(self, 'tax_uk')

        j.indextype = l2v(self, 'indextype')
        j.swap_counterparty = l2v(self, 'swap_counterparty')
        j.collateral_manager = l2v(self, 'collateral_manager')
        j.securities_lending = l2v(self, 'securities_lending')
        j.securities_lending_counterparty = l2v(self, 'securities_lending_counterparty')

        return j


class EtfCategoryItem(Item):
    """
    EtfCategoryItem represents the category and/or a subcategory of an ETF.
    """
    isin = Field()
    category = Field()


def l2v(item, key: str):
    if isinstance(item[key], list):
        return None if not item[key] else item[key][0]
    else:
        return None if item[key] == '-' or item[key] == '--' else item[key]
