#!/usr/bin/python3
import logging
import os
import sys
from getpass import getpass

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from db.dbconnector import db_connect, drop_static_tables
from extraetf import Extraetf
from isin_extractor import extract_isins_from_db

from etf_history import save_history
# todo db security?


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


def update_line(key, value):
    file = os.path.join("scraping", "settings.py")
    with open(file, 'r') as read_settings:
        lines = read_settings.readlines()
        for i, line in enumerate(lines):
            if line.find(key) != -1:
                lines[i] = value
                break

        with open(file, 'w') as write_settings:
            write_settings.writelines(lines)


def change_db_uri():
    old_uri = get_project_settings().get("SQL_URI")
    parts = old_uri.split(':')
    user_def = parts[1].split('/')[2]
    pw_def = parts[2].split('@')[0]
    host_def = parts[2].split('@')[1]
    port_def = parts[3].split('/')[0]
    db_def = parts[3].split('/')[1]

    print("If you do not enter anything, the current value from settings.py will be taken as default!")
    user = input(f"User? (default: {user_def})\n")
    pw = getpass("Password?\n")
    host = input(f"Host? (default: {host_def})\n")
    port = input(f"Port? (default: {port_def})\n")
    db = input(f"Database Name? (default: {db_def})\n")

    user = user_def if not user.strip() else user.strip()
    pw = pw_def if not pw.strip() else pw.strip()
    host = host_def if not host.strip() else host.strip()
    port = port_def if not port.strip() else port.strip()
    db = db_def if not db.strip() else db.strip()

    uri = f"SQL_URI = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'\n"
    update_line("SQL_URI", uri)


@click.group()
def cli():
    pass


@cli.command()
def setupdb():
    """Sets up the db connection."""
    change_db_uri()
    click.echo("Successfully change db configuration!")

@cli.command()
def setupi():
    """Runs the project setup interactively. Please use this option if you are unsure!
    This is the recommended way, as it ensures correct ordering of running the crawlers."""

    uri = get_project_settings().get("SQL_URI")
    if not uri:
        click.echo("You have not configured a db connection.")
        click.echo("Please ensure first you have correctly installed PostgreSQL\n" +
                "1) Windows Launch SQL Shell (psql) from the application launcher and check with 'SELECT version();'"
                "2) Linux: Run 'psql --version' from your CLI")
        click.echo("Once you are done you will be prompted in the following with the parameters for your db connection.")
        if prompt("Continue?"):
            change_db_uri()
        else:
            click.echo('Aborted db setup. Exiting.')
            return

    click.echo("For rerunning crawler static ETF data must be deleted first.")
    click.echo("Warning! This will permanently delete any static ETF data.")
    if prompt("Delete static ETF data?"):
        drop_static_data()

    if prompt("Run justetf crawler?"):
        crawl_justetf()

    if prompt("Run extraetf crawler?"):
        crawl_extraetf()


@cli.command()
def drop_static_data():
    """Deletes tables holding static ETF data."""
    drop_static_tables(db_connect())
    click.echo('Successfully dropped tables.')


@cli.command()
def crawl_extraetf():
    """Runs the extraetf crawler."""
    extraetf = Extraetf()
    extraetf.collect_data()

    click.echo('Finished crawling extraetf.com')


@cli.command()
def crawl_justetf():
    """Runs the justetf crawler."""
    try:
        run_crawler('justetf')
        click.echo('Finished crawling the justetf.com website.')
    except:
        click.echo('Failed crawling the justetf.com website.')
        raise


@cli.command()
@click.option('--outfile', '-o', default='extracted_isins.csv', help='output file for extracted isins')
def extract_isins(outfile):
    """Extracts all ISINS from db to a csv file."""
    extract_isins_from_db(outfile)


@cli.command()
@click.option('--historyfile', '-h', default='etf_history.csv', help='csv file containing etf history (output from Refinitiv)')
@click.option('--isinfile', '-i', default='isin.csv', help='helper csv file containing isins')
def import_history(historyfile, isinfile):
    """Extracts historic etf data from Refinitiv (Thomson Reuters)."""
    save_history(historyfile, isinfile)


if __name__ == '__main__':
    set_log_level(logging.INFO)
    cli()

