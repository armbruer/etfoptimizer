import logging
import os
import subprocess
import sys

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy import MetaData

import config
from db import sql_engine
from db.table_manager import drop_static_tables
from etf_history_api import save_history_api
from etf_history_excel import save_history_excel
from extraetf import Extraetf
from frontend.app import run_gui
from isin_extractor import extract_isins_from_db


class AsciiArtGroup(click.Group):
    def format_help(self, ctx, formatter):
        click.echo("""
 _____ _    __   _____       _   _           _
|  ___| |  / _| |  _  |     | | (_)         (_)
| |__ | |_| |_  | | | |_ __ | |_ _ _ __ ___  _ _______ _ __
|  __|| __|  _| | | | | '_ \| __| | '_ ` _ \| |_  / _ \ '__|
| |___| |_| |   \ \_/ / |_) | |_| | | | | | | |/ /  __/ |
\____/ \__|_|    \___/| .__/ \__|_|_| |_| |_|_/___\___|_|
                      | |
                      |_|
    """)
        super().format_help(ctx, formatter)


def set_log_level(level):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    root.addHandler(handler)


def run_crawler(name: str):
    process = CrawlerProcess(get_project_settings())
    process.crawl(name)
    process.start()


@click.group(cls=AsciiArtGroup)
def etfopt():
    pass


@etfopt.command()
def drop_static_data():
    """
    Deletes tables holding static ETF data
    """
    drop_static_tables(sql_engine)
    click.echo('Successfully dropped tables')


@etfopt.command()
def crawl_extraetf():
    """
    Runs a crawler for retrieving data from extraetf.com
    """
    click.echo("Starting to crawl extraetf.com. Wait until you see the finish message. This might take a while ...")
    extraetf = Extraetf()
    extraetf.collect_data()

    click.echo('Finished crawling extraetf.com')


@etfopt.command()
def crawl_justetf():
    """
    Runs a crawler for retrieving data from justetf.com
    """
    try:
        click.echo("Starting to crawl justetf.com. Wait until you see the finish message. This might take a while ...")
        run_crawler('justetf')
        click.echo('Finished crawling the justetf.com website')
    except:
        click.echo('Failed crawling the justetf.com website')
        raise


@etfopt.command()
@click.option('--outfile', '-o', default='extracted_isins.xlsx', help='output file for extracted isins')
def extract_isins(outfile):
    """
    Extracts all ISINS from db to a csv file
    """
    extract_isins_from_db(outfile)
    click.echo(f"Wrote ISINs into {outfile}")


@etfopt.command()
@click.option('--historyfile', '-h', default='etf_history.csv',
              help='csv file containing etf history (output from Refinitiv)')
@click.option('--isinfile', '-i', default='isin.csv', help='helper csv file containing isins')
def import_history_excel(historyfile, isinfile):
    """
    Retrieves historic etf data from Refinitiv (Excel)
    """
    click.echo("Getting etf history...")
    save_history_excel(historyfile, isinfile)
    click.echo('Finished retrieving etf history')


@etfopt.command()
def import_history_api():
    """
    Retrieves historic etf data from Refinitiv (API)
    """
    click.echo("Getting etf history...")
    save_history_api()
    click.echo('Finished retrieving etf history')


@etfopt.command()
@click.option('--file', '-f', default='backup.sql', help='path to database import file')
def import_db(file):
    """
    Imports the etf database from a file
    """
    filepath = os.path.realpath(file)
    if not os.path.isfile(file):
        click.echo(f"Importing failed: could not find the file {filepath}")
        return

    result = ''
    if click.confirm("Warning: This will delete all data prior to importing. Do you want to continue?"):
        # drop all tables
        meta = MetaData()
        meta.bind = sql_engine
        meta.reflect()
        meta.drop_all()

        try:
            result = subprocess.check_output(
                ['psql', '-d', config.get_sql_uri(nodriver=True), '-f', f'{filepath}'])
            click.echo("Etf database was imported successfully")
        except subprocess.CalledProcessError:
            click.echo("Importing the etf database failed")
        click.echo(result)
    else:
        click.echo("Import aborted")


@etfopt.command()
def export_db():
    """
    Exports the etf database into a file
    """
    filepath = 'backup.sql'
    result = ''

    try:
        result = subprocess.check_output(['pg_dump', '-d', config.get_sql_uri(nodriver=True), '-f', filepath])
        click.echo(f"Etf database was exported successfully into the file '{os.getcwd()}/{filepath}'")
    except subprocess.CalledProcessError:
        click.echo("Exporting the etf database failed")

    click.echo(result)


@etfopt.command()
def start_gui():
    """
    Starts the graphical user interface
    """
    run_gui()


if __name__ == '__main__':
    set_log_level(logging.WARNING)
    etfopt()
