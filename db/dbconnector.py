
import sys

import click
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None


def db_connect():
    """
    Performs db connection using db settings from settings.py.
    Returns sqlalchemy engine instance
    """
    global engine
    if engine is None:
        uri = get_project_settings().get("SQL_URI")
        if not uri:
            click.echo("Please setup the db connection first!")
            sys.exit(1)
        engine = create_engine(uri)
    return engine


def create_table(engine):
    """
    Creates the tables if they do not exist.
    """
    # unused models imports are required for sqlalchemy to create tables as expected
    from db.dbmodels import Etf, EtfHistory, EtfCategory, IsinCategory
    Base.metadata.create_all(engine)


def drop_static_tables(engine):
    """
    Drops all tables with static data.
    """
    from db.dbmodels import Etf, EtfCategory, IsinCategory
    Base.metadata.drop_all(bind=engine, tables=[Etf.__table__, IsinCategory.__table__, EtfCategory.__table__])


