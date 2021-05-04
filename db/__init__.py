import sys

import click
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

uri = get_project_settings().get("SQL_URI")
if uri is None:
    click.echo("Could not find SQL_URI in settings.py. Please set up a valid URI first.")
    sys.exit(1)

sql_engine = create_engine(uri)
Session = sessionmaker(bind=sql_engine)
