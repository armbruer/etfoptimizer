import logging
import sys

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from db import sql_engine
from db.table_manager import drop_static_tables
from etf_history_excel import save_history
from extraetf import Extraetf
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


def prompt(ask):
    return input(ask + " [y|n]\n>>> ").lower().strip()[0] == 'y'


def run_crawler(name: str):
    process = CrawlerProcess(get_project_settings())
    process.crawl(name)
    process.start()


@click.group(cls=AsciiArtGroup)
def etfopt():
    pass


@etfopt.command()
def drop_static_data():
    """Deletes tables holding static ETF data."""
    drop_static_tables(sql_engine)
    click.echo('Successfully dropped tables.')


@etfopt.command()
def crawl_extraetf():
    """Runs the extraetf crawler."""
    extraetf = Extraetf()
    # TODO fix no logging output...
    extraetf.collect_data()

    click.echo('Finished crawling extraetf.com')


@etfopt.command()
def crawl_justetf():
    """Runs the justetf crawler."""
    try:
        run_crawler('justetf')
        click.echo('Finished crawling the justetf.com website.')
    except:
        click.echo('Failed crawling the justetf.com website.')
        raise


@etfopt.command()
@click.option('--outfile', '-o', default='extracted_isins.xlsx', help='output file for extracted isins')
def extract_isins(outfile):
    """Extracts all ISINS from db to a csv file."""
    extract_isins_from_db(outfile)


@etfopt.command()
@click.option('--historyfile', '-h', default='etf_history.csv',
              help='csv file containing etf history (output from Refinitiv)')
@click.option('--isinfile', '-i', default='isin.csv', help='helper csv file containing isins')
def import_history(historyfile, isinfile):
    """Extracts historic etf data from Refinitiv (Thomson Reuters)."""
    save_history(historyfile, isinfile)


if __name__ == '__main__':
    set_log_level(logging.INFO)
    etfopt()
