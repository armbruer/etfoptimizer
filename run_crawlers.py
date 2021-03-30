#!/usr/bin/python3
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from getpass import getpass

from dbconnector import drop_static_tables, db_connect
from etf_categories import save_categories
from isin_extractor import extract_isins
import os


def prompt(ask):
    return input(ask + " [y|n]\n").lower().strip()[0] == 'y'
# todo avoid having so many engine
# todo database security?
# todo maybe some command line options?


def update_line(key, value):
    file = os.path.join("ETFOptimizer", "settings.py")
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
    print("Successfully change database configuration!")


if prompt("Change database configuration?"):
    change_db_uri()

print("Deleting the static (scraped) etf data is required if you want to run again the same crawler.")
print("WARNING: If you do not apply this step and you run a particular crawler again you will see errors!")
print("WARNING: This will permanently delete your data in several tables holding static etf data!")
if prompt("Delete static etf data?"):
    drop_static_tables(db_connect())
    print("Deleted static tables.")

if prompt("Run justetf crawler?"):
    # 1. Crawl jusetetf.com
    process = CrawlerProcess(get_project_settings())
    process.crawl('justetf')
    process.start()

if prompt("Run extraetf crawler?"):
    # 2. Crawl extraetf.com
    process = CrawlerProcess(get_project_settings())
    process.crawl('extraetf')
    process.start()

if prompt("Run extraetf categories crawler?"):
    # 3. Save known categories from extraetf.com
    save_categories()

    # 4. Crawl extraetf again, this time for categories of already crawled etfs.
    process = CrawlerProcess(get_project_settings())
    process.crawl('extraetf_categories')
    process.start()

if prompt("Write ISINs to a .csv?"):
    # 5. Extract ISINs and write to .csv
    res = input("ISIN Output file?")
    out_file = None if not res.strip() else res.strip()
    extract_isins(out_file)
