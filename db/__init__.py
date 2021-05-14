import sys

import click
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()
config.create_if_not_exists()
config.read_config()

uri = config.get_sql_uri()  # TODO check if uri is default -> print warning this might not work
if uri is None:
    click.echo(
        "Could not read sql uri from etfoptimizer.ini. Please set the values in the database-uri section accordingly.")
    sys.exit(1)

sql_engine = create_engine(uri)
Session = sessionmaker(bind=sql_engine)
