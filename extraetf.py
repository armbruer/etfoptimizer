import logging
import time

import requests
from sqlalchemy.exc import IntegrityError

from db import sql_engine, Session
from db.models import EtfCategory, IsinCategory, Etf
from db.table_manager import create_table
from scraping.items import EtfItem, string_to_date


class Extraetf():

    def __init__(self):
        self.category_types = {'sector_name': 'Sektor', 'land_name': 'Land', 'region_name': 'Region',
                               'asset_class_name': "Asset Klasse", 'strategy_name': 'Strategie',
                               'fund_currency_id': 'Währung',
                               'bond_type_name': 'Anlageart', 'commodity_class_name': 'Rohstoffklasse',
                               'bond_maturity_name': 'Laufzeit',
                               'bond_rating_name': 'Rating'}
        create_table(sql_engine)
        self.session = Session()
        self.cgry_cache = dict()

    def collect_data(self):
        offset = 0
        limit = 200

        while True:
            params = {'offset': offset, 'limit': limit, 'ordering': '-assets_under_management', 'leverage_from': 1,
                      'leverage_to': 1}
            response = requests.get('https://de.extraetf.com/api-v2/search/full/', params=params)
            time.sleep(2)

            data = response.json()
            page = int(offset / limit + 1)
            results = data['results']
            logging.info(f"Extracted etfs from page {page}!")
            self.parse_page(results)

            if data['next'] is None:
                break

            offset += limit

        self.session.close()

    def parse_page(self, results):
        for result in results:
            detail_params = {'isin': result['isin']}
            detail_response = requests.get('https://de.extraetf.com/api-v2/detail/', detail_params)
            detail_result = detail_response.json()['results'][0]

            item = self.parse_item(result, detail_result)
            item = self.process_item(item)
            self.save_item(item)

            self.save_item_categories(result, detail_result)

            time.sleep(0.25)  # slow down to avoid getting banned :)

    def parse_item(self, result, detail_result):
        item = EtfItem()
        for field in item.fields:
            item.setdefault(field, None)

        item['name'] = result['fondname']
        item['isin'] = result['isin']
        item['wkn'] = result['wkn']
        item['ter'] = result['ter']
        logging.info(f"Parsing ETF '{result['isin']}'")

        replication = detail_result['replication_methodology_first_level']
        repl_detail = detail_result['replication_methodology_second_level']
        if repl_detail is not None:
            replication = repl_detail if replication is None else '(' + repl_detail + ')'

        item['replication'] = replication
        item['distribution_policy'] = result['distribution_policy']
        item['fund_size'] = result['assets_under_management']
        item['inception'] = result['launch_date']
        item['fund_currency'] = result['fund_currency_id']
        item['fund_domicile'] = result['fund_domicile']

        item['fund_provider'] = detail_result['provider_name']
        item['legal_structure'] = result['legal_structure']
        item['fund_structure'] = detail_result['fund_structure']
        item['ucits_compliance'] = detail_result['ucits_konform']
        item['administrator'] = detail_result['administrator']
        item['revision_company'] = detail_result['auditor_company']
        item['custodian_bank'] = detail_result['depotbank']
        item['tax_germany'] = detail_result['tax_status_de']
        item['tax_switzerland'] = detail_result['tax_status_ch']
        item['tax_austria'] = detail_result['tax_status_au']
        item['tax_uk'] = detail_result['tax_status_uk']
        item['distribution_frequency'] = detail_result['distribution_interval']

        item['volatility_one_year'] = detail_result['volatility_1_year']
        item['fiscal_year_end_month'] = detail_result['fiscal_year_end_month']
        item['indextype'] = detail_result['index_type']
        item['swap_counterparty'] = detail_result['swap_counterparty']
        item['collateral_manager'] = detail_result['collateral_manager']
        item['securities_lending'] = detail_result['has_securities_lending']
        item['securities_lending_counterparty'] = detail_result['securities_lending_party']

        item['net_assets_currency'] = detail_result['net_assets_currency']
        item['is_accumulating'] = detail_result['is_accumulating']
        item['is_derivative_based'] = detail_result['is_derivative_based']
        item['is_distributing'] = detail_result['is_distributing']
        item['is_etc'] = detail_result['is_etc']
        item['is_etf'] = detail_result['is_etf']
        item['is_hedged'] = detail_result['is_hedged']
        item['hedged_currency'] = detail_result['is_hedged_currency']
        item['is_index_fund'] = detail_result['is_index_fund']
        item['is_leveraged'] = detail_result['is_leveraged']
        item['is_physical_full'] = detail_result['is_physical_full']
        item['is_short'] = detail_result['is_short']
        item['is_socially_responsible_fund'] = detail_result['is_socially_responsible_fund']
        item['is_structured'] = detail_result['is_structured']
        item['is_swap_based_etf'] = detail_result['is_swap_based_etf']
        item['is_synthetic_replication'] = detail_result['is_synthetic_replication']

        return item

    def process_item(self, item):
        item['inception'] = string_to_date(item['inception'])

        return item

    def save_item(self, item: EtfItem):
        etf = item.to_etfitemdb()
        try:
            current_data: Etf = self.session.query(Etf).filter_by(isin=etf.isin).first()
            if current_data is not None:
                logging.info(f"Updating existing ETF {current_data.isin}")
                self.update_item(current_data, etf)

            else:
                self.session.add(etf)
                self.session.commit()
        except:
            logging.warning(f"Could not save data for {etf.isin}!")
            self.session.rollback()
            raise

    def update_item(self, current_data, etf):
        # we only update attributes that do not exist at justetf.com or are of higher precision at extraetf.com
        # higher precision
        current_data.fund_size = etf.fund_size
        current_data.ter = etf.ter
        # new
        current_data.tax_germany = etf.tax_germany
        current_data.net_assets_currency = etf.net_assets_currency
        current_data.is_accumulating = etf.is_accumulating
        current_data.is_derivative_based = etf.is_derivative_based
        current_data.is_distributing = etf.is_distributing
        current_data.is_etc = etf.is_etc
        current_data.is_etf = etf.is_etf
        current_data.is_hedged = etf.is_hedged
        current_data.hedged_currency = etf.hedged_currency
        current_data.is_index_fund = etf.is_index_fund
        current_data.is_leveraged = etf.is_leveraged
        current_data.is_physical_full = etf.is_physical_full
        current_data.is_short = etf.is_short
        current_data.is_socially_responsible_fund = etf.is_socially_responsible_fund
        current_data.is_structured = etf.is_structured
        current_data.is_swap_based_etf = etf.is_swap_based_etf
        current_data.is_synthetic_replication = etf.is_synthetic_replication
        self.session.commit()

    def save_item_categories(self, result, detail_result):
        isin = result['isin']
        categories = [(detail_result[cat_key], cat_type) for cat_key, cat_type in self.category_types.items()]

        try:
            for cat_name, cat_type in categories:
                self.save_item_category(cat_name, cat_type, isin)

        except:
            logging.warning(f"Could not save data for {result['isin']}!")
            self.session.rollback()
            raise

    def save_item_category(self, cat_name, cat_type, isin):
        if cat_name is not None and cat_name:
            if cat_name in self.cgry_cache:
                # if category has already been added to db we can use the cache to retrieve its id
                cat_id = self.cgry_cache[cat_name]
            else:
                cat_id = self.add_category(cat_name, cat_type)
            if cat_id:
                ic = IsinCategory()
                ic.etf_isin = isin
                ic.category_id = cat_id

                try:
                    self.session.add(ic)
                    self.session.commit()
                except IntegrityError:
                    logging.warning(f"Could not insert category data for ETF with ISIN {isin} and category {cat_name} "
                                    f"as it already exists!")
                    self.session.rollback()

            else:
                logging.error(f"No ID was found for item with category {cat_name}")

    def add_category(self, cat_name, cat_type):
        etf_category = EtfCategory()
        etf_category.name = cat_name
        etf_category.type = cat_type
        self.session.add(etf_category)
        self.session.commit()
        self.session.refresh(etf_category)  # refresh to get auto-incremented cat_id
        cat_id = etf_category.id
        self.cgry_cache[cat_name] = cat_id
        return cat_id
