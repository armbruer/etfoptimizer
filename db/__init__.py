import sys

import click
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

import config

# Create and load the config at startup
# Connect to the SQL database
Base = declarative_base()
config.create_if_not_exists()
config.read_config()

uri = config.get_sql_uri()
if uri is None:
    click.echo(
        "Could not read sql uri from etfoptimizer.ini. Please set the values in the database-uri section accordingly.")
    sys.exit(1)

if config.get_value('database-uri', 'username') == "<username>" or config.get_value('database-uri',
                                                                                    'password') == "<password>":
    click.echo("Please make sure to configure your database connection in etfoptimizer.ini first. At minimum you need "
               "to replace values of the format <...> with the expected values. You should find the file in "
               "~/.config/etfoptimizer on Linux and in C::\\Users\\<windows user>\\AppData\\Local\\etfoptimizer\\Config. If you need further assistance, please read documentation.pdf")
    sys.exit(1)

sql_engine = create_engine(uri)
if not database_exists(sql_engine.url):
    create_database(sql_engine.url)

Session = sessionmaker(bind=sql_engine)
