# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging

# useful for handling different item types with a single interface
from scrapy.exceptions import DropItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from ETFOptimizer.items import l2v
from dbconnector import db_connect, create_table, Etf, IsinCategory


class EtfPipeline:

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        etf = item.to_etfitemdb()
        logging.info(f"Preparing to save {etf.name} in database")

        try:
            etf_current = self.session.query(Etf)
            exists = etf_current.filter_by(isin=etf.isin).first() is not None
            if exists:
                logging.warning(f"{etf.name} is already in saved in database. "
                                f"Updated values are not reflected in database. "
                                f"Please delete the table 'etfs' to get fresh values into the database!")
            else:
                self.session.add(etf)
                self.session.commit()
        except:
            logging.warning(f"Could not save data for {etf.name}!")
            self.session.rollback()
            raise

        return item

