# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import locale
from datetime import datetime

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Field, Item
from scrapy.loader import ItemLoader

from db.models import Etf


def string_to_bool(x: str):
    """
    Converts a string to a boolean.
    """
    x = x.strip().lower()
    if x == 'ja' or x == 'yes':
        return True
    elif x == 'nein' or x == 'no':
        return False
    else:
        return None


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
            s = s.replace(',', '.')
            res = float(s) / 100
            break
        except:
            continue

    return res


date_formats = [('en_US.utf8', '%d. %B %Y'), ('de_DE.utf8', '%d. %B %Y'), ('en_US.utf8', '%Y-%m-%d')]


def string_to_date(x: str):
    """
    Converts a string date of format 01 January 1999 into a date.
    """
    res = None
    for format in date_formats:
        lang, f = format
        try:
            locale.setlocale(locale.LC_ALL, lang)
            res = datetime.strptime(x, f)
            break
        except ValueError:
            pass  # continue conversion tries

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

    month_to_int = lambda x: int(x.split(' ')[0].replace('.', '')) if len(x.split(' ')) > 1 else x
    fiscal_year_end_month_in = MapCompose(empty_to_none, month_to_int)
    ucits_compliance_in = MapCompose(string_to_bool)
    securities_lending_in = MapCompose(string_to_bool)
    benchmark_index_in = MapCompose(str.strip)
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

    # other
    benchmark_index = Field()

    # legal structure
    fund_structure = Field()
    ucits_compliance = Field()
    fund_provider = Field()
    administrator = Field()
    investment_advisor = Field()
    custodian_bank = Field()
    revision_company = Field()
    fiscal_year_end_month = Field()
    swiss_representative = Field()
    swiss_paying_agent = Field()

    # tax status
    tax_germany = Field()
    tax_switzerland = Field()
    tax_austria = Field()
    tax_uk = Field()

    # replica,swap,securities lending
    indextype = Field()
    swap_counterparty = Field()
    collateral_manager = Field()
    securities_lending = Field()
    securities_lending_counterparty = Field()

    net_assets_currency = Field()
    is_accumulating = Field()
    is_derivative_based = Field()
    is_distributing = Field()
    is_etc = Field()
    is_etf = Field()
    is_hedged = Field()
    hedged_currency = Field()
    is_index_fund = Field()
    is_leveraged = Field()
    is_physical_full = Field()
    is_short = Field()
    is_socially_responsible_fund = Field()
    is_structured = Field()
    is_swap_based_etf = Field()
    is_synthetic_replication = Field()

    def to_etfitemdb(self) -> Etf:
        """Converts an EtfItem into a JustetfItem.
        The purpose is to convert from a scrapy representation to an sqlalchemy representation of the same item,
        so the item can be stored in a db"""

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
        j.fiscal_year_end_month = l2v(self, 'fiscal_year_end_month')
        j.swiss_representative = l2v(self, 'swiss_representative')
        j.swiss_paying_agent = l2v(self, 'swiss_paying_agent')

        j.tax_germany = l2v(self, 'tax_germany')
        j.tax_switzerland = l2v(self, 'tax_switzerland')
        j.tax_austria = l2v(self, 'tax_austria')
        j.tax_uk = l2v(self, 'tax_uk')

        j.indextype = l2v(self, 'indextype')
        j.swap_counterparty = l2v(self, 'swap_counterparty')
        j.collateral_manager = l2v(self, 'collateral_manager')
        j.securities_lending = l2v(self, 'securities_lending')
        j.securities_lending_counterparty = l2v(self, 'securities_lending_counterparty')

        j.net_assets_currency = l2v(self, 'net_assets_currency')
        j.is_accumulating = l2v(self, 'is_accumulating')
        j.is_derivative_based = l2v(self, 'is_derivative_based')
        j.is_distributing = l2v(self, 'is_distributing')
        j.is_etc = l2v(self, 'is_etc')
        j.is_etf = l2v(self, 'is_etf')
        j.is_hedged = l2v(self, 'is_hedged')
        j.hedged_currency = l2v(self, 'hedged_currency')
        j.is_index_fund = l2v(self, 'is_index_fund')
        j.is_leveraged = l2v(self, 'is_leveraged')
        j.is_physical_full = l2v(self, 'is_physical_full')
        j.is_short = l2v(self, 'is_short')
        j.is_socially_responsible_fund = l2v(self, 'is_socially_responsible_fund')
        j.is_structured = l2v(self, 'is_structured')
        j.is_swap_based_etf = l2v(self, 'is_swap_based_etf')
        j.is_synthetic_replication = l2v(self, 'is_synthetic_replication')

        return j


def l2v(item, key: str):
    if isinstance(item[key], list):
        return None if not item[key] else item[key][0]
    else:
        return None if item[key] == '-' or item[key] == '--' else item[key]
