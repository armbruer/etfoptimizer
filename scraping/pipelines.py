# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging

from db import sql_engine, Session
from db.models import Etf
from db.table_manager import create_table


class EtfPipeline:

    def __init__(self):
        create_table(sql_engine)

    def open_spider(self, spider):
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        """
        Converts each extracted item from a scrapy item into an sqlalchemy item, then stores it in the database.
        """
        etf = item.to_etfitemdb()
        logging.info(f"Preparing to save {etf.name} in database")

        try:
            etf_current = self.session.query(Etf)
            exists = etf_current.filter_by(isin=etf.isin).first() is not None
            if exists:
                logging.warning(f'Updated values are not reflected in database for values scraped from justetf.com. '
                                f'Please delete this table if you want to get fresh values into the database and '
                                f'ensure extraetf.com is first scraped.')
            else:
                self.session.add(etf)
                self.session.commit()
        except:
            logging.warning(f"Could not save data for {etf.name}!")
            self.session.rollback()
            raise

        return item
