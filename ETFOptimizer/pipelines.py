# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import logging

from dbmapper import StaticETFs


class JustetfPipeline:

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user=crawler.settings.get('POSTGRE_USER'),
            password=crawler.settings.get('POSTGRE_PASSWORD'),
            host=crawler.settings.get('POSTGRE_HOST'),
            port=crawler.settings.get('POSTGRE_PORT'),
            database=crawler.settings.get('POSTGRE_DB', 'justetf'),
        )

    def open_spider(self, spider):
        self.engine = create_engine(f'postgresql+psycopg2://{self.user}:{self.password}'
                                    f'@{self.host}:{self.port}/{self.database}')
        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logging.info(f"Opened connection to database")
        self.password = ""  # todo

    def close_spider(self, spider):
        self.session.commit()
        self.session.flush()
        logging.info(f"Saved all items in database")
        self.engine.dispose()  # todo


    def process_item(self, item, spider):
        etf = StaticETFs.fromItem(item)
        self.session.add(etf)
        logging.info(f"Preparing to save {item['name']} in database")

        return item
