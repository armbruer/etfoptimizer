#!/usr/bin/python3
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dbconnector import drop_static_tables, db_connect
from etf_categories import save_categories
from isin_extractor import extract_isins


def prompt(ask):
    return input(ask + " [y|n]\n").lower().strip()[0] == 'y'
# todo before continuing please make sure to have read xyz
# todo nice feature: change the database uri from cli?
# todo avoid having so many engine
# todo fix problem when running from command line
# todo fix not respecting settings in settings.py? e.g. DEBUG as LOG_LEVEL


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
