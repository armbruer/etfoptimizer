import logging
import time

import requests
from sqlalchemy.orm import sessionmaker

from ETFOptimizer.items import EtfItem, string_to_date, strip_float
from dbconnector import create_table, db_connect, Etf, IsinCategory


class Extraetf():

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def collect_data(self):
        offest = 0
        params = {'offset': offest, 'limit': 200, 'ordering': '-assets_under_management', 'leverage_from': 1, 'leverage_to': 1}
        while True:
            response = requests.get('https://de.extraetf.com/api-v2/search/full/', params)
            time.sleep(2)
            data = response.json()
            results = data['results']

            logging.info(f"Extracted etfs from page {offest % 200 + 1}!")

            for result in results:
                detail_params = {'isin': result['isin']}
                detail_response = requests.get('https://de.extraetf.com/api-v2/detail/', detail_params)
                detail_result = detail_response.json()['results'][0]

                item = self.parse_item(result, detail_result)
                item = self.process_item(item)
                self.save_item(item)

                self.save_item_categories(result)

                time.sleep(0.25)  # slow down to avoid getting banned :)

            if data['next'] is None:
                break

            offest += 200

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

        # main_data table
        item['ter'] = result['ter']
        item['replication'] = result['replication_methodology_first_level']  # TODO
        item['distribution_policy'] = result['distribution_policy']
        item['fund_size'] = result['assets_under_management']
        item['inception'] = result['launch_date']
        item['fund_currency'] = result['fund_currency_id']
        item['fund_domicile'] = result['fund_domicile']

        # TODO MISSING VALUES
        item['fund_provider'] = None
        item['legal_structure'] = result['legal_structure']
        item['fund_structure'] = detail_result['fund_structure']
        item['ucits_compliance'] = detail_result['ucits_konform']
        item['administrator'] = detail_result['administrator']
        item['revision_company'] = None
        item['custodian_bank'] = None
        item['tax_germany'] = detail_result['tax_status_de']
        item['tax_switzerland'] = detail_result['tax_status_ch']
        item['tax_austria'] = detail_result['tax_status_au']
        item['tax_uk'] = detail_result['tax_status_uk']
        item['tax_data'] = None
        item['distribution_frequency'] = detail_result['distribution_interval']

        item['benchmark_index'] = None
        item['investment_advisor'] = None
        item['strategy_risk'] = None
        item['volatility_one_year'] = None
        item['currency_risk'] = None
        item['fiscal_year_end'] = None
        item['swiss_representative'] = None
        item['swiss_paying_agent'] = None
        item['indextype'] = None
        item['swap_counterparty'] = None
        item['collateral_manager'] = None
        item['securities_lending'] = None
        item['securities_lending_counterparty'] = None

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

    def save_item_categories(self, result):
        isin = result['isin']
        categories = [result['sector_name'], result['land_name'], result['region_name'], result['asset_class_name']]

        try:
            for category in categories:
                if category is not None and category:
                    ic = IsinCategory()
                    ic.category = category
                    ic.etf_isin = isin
                    self.session.add(ic)
            self.session.commit()
        except: # todo better exception handling?
            logging.warning(f"Could not save data for {result['isin']}!")
            self.session.rollback()
            raise
