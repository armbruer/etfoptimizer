import sys

import click
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

import config

Base = declarative_base()
config.create_if_not_exists()
config.read_config()

uri = config.get_sql_uri()
if uri is None:
    click.echo(
        "Could not read sql uri from etfoptimizer.ini. Please set the values in the database-uri section accordingly.")
    sys.exit(1)

sql_engine = create_engine(uri)
if not database_exists(sql_engine.url):
    create_database(sql_engine.url)

Session = sessionmaker(bind=sql_engine)
