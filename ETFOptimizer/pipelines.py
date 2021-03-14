# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging

# useful for handling different item types with a single interface
from sqlalchemy.orm import sessionmaker

from dbconnector import db_connect, create_table

class JustetfPipeline:

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()


    def process_item(self, item, spider):
        etf = item.to_justetf_item()
        logging.info(f"Preparing to save {etf.name} in database")

        try:
            # TODO query first to check if entry already exists!
            self.session.add(etf)
            self.session.commit()
        except:
            self.session.rollback()
            raise

        return item
