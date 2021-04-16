import logging
import time

import requests
from sqlalchemy.orm import sessionmaker

from db.dbmodels import EtfCategory, IsinCategory, Etf
from scraping.items import EtfItem, string_to_date
from db.dbconnector import create_table, db_connect


class Extraetf():

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.category_types = {'sector_name': 'Sektor', 'land_name': 'Land', 'region_name': 'Region',
                       'asset_class_name': "Asset Klasse", 'strategy_name': 'Strategie', 'fund_currency_id': 'Währung',
                       'bond_type_name': 'Anlageart', 'commodity_class_name': 'Rohstoffklasse', 'bond_maturity_name': 'Laufzeit',
                       'bond_rating_name': 'Rating'}
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.cgry_cache = dict()

    def collect_data(self):
        params = {'offset': 0, 'limit': 200, 'ordering': '-assets_under_management', 'leverage_from': 1, 'leverage_to': 1}
        while True:
            response = requests.get('https://de.extraetf.com/api-v2/search/full/', params)
            time.sleep(2)
            data = response.json()
            results = data['results']

            logging.info(f"Extracted etfs from page {params['offset'] % 200 + 1}!")

            for result in results:
                detail_params = {'isin': result['isin']}
                detail_response = requests.get('https://de.extraetf.com/api-v2/detail/', detail_params)
                detail_result = detail_response.json()['results'][0]

                item = self.parse_item(result, detail_result)
                item = self.process_item(item)
                self.save_item(item)

                self.save_item_categories(result, detail_result)

                time.sleep(0.25)  # slow down to avoid getting banned :)

            if data['next'] is None:
                break
            break  # TODO REMOVE, only for debugging
            params['offset'] += 200

        self.session.close()


    def parse_item(self, result, detail_result):
        name = result['fondname']
        logging.info(f"Parsing ETF '{name}'")

        item = EtfItem()
        for field in item.fields:
            item.setdefault(field, None)

        item['name'] = name
        item['isin'] = result['isin']
        item['wkn'] = result['wkn']
        item['ter'] = result['ter']

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
            current_data = self.session.query(Etf).filter_by(isin=etf.isin).first()
            if current_data is not None:
                current_data.fund_size = etf.fund_size
                current_data.ter = etf.ter
                current_data.tax_germany = etf.tax_germany

                self.session.commit()

            else:
                self.session.add(etf)
                self.session.commit()
        except:
            logging.warning(f"Could not save data for {etf.name}!")
            self.session.rollback()
            raise

    def save_item_categories(self, result, detail_result):
        isin = result['isin']
        categories = [(detail_result[cat_key], cat_type) for cat_key, cat_type in self.category_types.items()]

        try:
            for cat_name, cat_type in categories:
                if cat_name is not None and cat_name:
                    cat_id = None
                    if cat_name in self.cgry_cache:
                        cat_id = self.cgry_cache[cat_name]
                    else:
                        etf_category = EtfCategory()
                        etf_category.name = cat_name
                        etf_category.type = cat_type
                        self.session.add(etf_category)
                        self.session.commit()
                        self.session.refresh(etf_category)  # refresh to get auto-incremented cat_id

                        cat_id = etf_category.id
                        self.cgry_cache[cat_name] = cat_id

                    if cat_id:
                        ic = IsinCategory()
                        ic.etf_isin = isin
                        ic.category_id = cat_id
                        self.session.add(ic)
                    else:
                        logging.error(f"No ID was found for item with category {cat_name}")

            self.session.commit()  # only commit once after all categories of one item have been handled
        except:  # todo better exception handling?
            logging.warning(f"Could not save data for {result['isin']}!")
            self.session.rollback()
            raise

