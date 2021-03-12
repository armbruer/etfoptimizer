import logging
import time

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from ETFOptimizer.items import EtfItem


def get_detail_table_values(selector, table_size):
    values = [selector.xpath('*[' + str(i) + ']/td[2]/text()').getall() for i in range(1, table_size + 1)]
    return values


class JustetfSpider(scrapy.Spider):
    name = 'justetf'
    allowed_domains = ['justetf.com']
    start_urls = ['https://justetf.com/de-en/find-etf.html']

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = webdriver.Chrome()

        # Use headless option to not open a new browser window
        #options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        #desired_capabilities = options.to_capabilities()
        #self.driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
        #self.driver.implicitly_wait(10)

    def parse(self, response, **kwargs):
        logging.info("Begin parsing ...")
        # load first page second time, this time through selenium
        self.driver.get(response.url)
        time.sleep(3)

        self.handleCookies()
        #self.increaseRows()

        pagenum = 1
        while True:
            time.sleep(2.5) # give enough time for updating contents inside selenium browser
            r = Selector(text=self.driver.page_source)
            for link in r.xpath('//tbody/tr[@role="row"]/td/a[@class="link"]/@href').getall():
                logging.info("Found link:" + link)
                yield Request(link, callback=self.parse_item)

            logging.info(f"Extracted etfs from page {pagenum}")
            pagenum += 1
            next_page = self.driver.find_element_by_xpath('//a[@id="etfsTable_next"]')
            if not next_page.is_enabled() or not next_page.is_displayed():
                break
            next_page.click()
        self.driver.close()
        logging.info("Finished parsing")

    def increaseRows(self):
        # reduce the number of page loads required for better throughput, and fewer requests
        try:
            show_rows_button = self.driver.find_element_by_xpath('//a/span[contains(text(), "Show 25 rows")]/..')
            show_rows_button.click()
            time.sleep(1)
            select_rows_button = self.driver.find_element_by_xpath('//a[contains(text(), "100 rows")]/..')
            select_rows_button.click()
            time.sleep(1)
        except NoSuchElementException:
            logging.warning("Could not find rows selector button. Continuing ... ")

    def handleCookies(self):
        try:
            # cookie settings: allow selection
            allow_selection_button = self.driver.find_element_by_xpath('//a[@id="CybotCookiebotDialogBodyLevel'
                                                                       'ButtonLevelOptinAllowallSelection"]')
            allow_selection_button.click()
            time.sleep(0.5)
        except NoSuchElementException:
            logging.warning("No cookie message was found. Continuing ...")

    def parse_item(self, response):
        # TODO nonstrings should be parsed properly
        isin_parent = response.xpath('//span[@class="vallabel" and .="ISIN"]/..')
        name = isin_parent.xpath('../*[1]/text()').getall()
        logging.info(f"Parsing ETF '{name}'")

        isin = isin_parent.xpath('*[2]/text()').getall()
        wkn = isin_parent.xpath('*[4]/text()').getall()

        item = EtfItem(name=name, isin=isin, wkn=wkn)
        item['ter'] = response.xpath('//div[@class="h5" and contains(text(), "Fees")]/../div[2]/div/div[1]/div['
                                     '1]/text()').getall()

        risk_parent = response.xpath('//div[@class="h5" and contains(text(), "Risk")]/..')

        item['fund_size'] = risk_parent.xpath('div[2]/div/div[1]/div[1]/text()').getall()
        risk_table = risk_parent.xpath('table/tbody')
        values = get_detail_table_values(risk_table, 7)
        item['replication'] = risk_table.xpath('*[1]/td[2]/span[1]/text()').getall()
        item['legal_structure'] = values[1]
        item['strategy_risk'] = values[2]
        item['fund_currency'] = values[3]
        item['currency_risk'] = values[4]
        item['volatility_one_year'] = risk_table.xpath('*[6]/td[2]/span[1]/text()').getall()
        item['inception'] = values[6]

        dividend_table = response.xpath('//div[@class="h5 margin-lineup" and contains(text(), "Dividend/ '
                                        'Taxes")]/../table/tbody')
        values = get_detail_table_values(dividend_table, 4)
        item['distribution_policy'] = values[0]
        item['distribution_frequency'] = values[1]
        item['fund_domicile'] = values[2]
        item['tax_data'] = dividend_table.xpath('*[4]/td[2]/a/@href').getall()

        legal_structure_table = response.xpath('//div[@class="h5" and contains(text(), "Legal '
                                               'structure")]/../table/tbody')
        values = get_detail_table_values(legal_structure_table, 10)
        item['fund_structure'] = values[0]
        item['ucits_compliance'] = values[1]
        item['fund_provider'] = values[2]
        item['administrator'] = values[3]
        item['investment_advisor'] = values[4]
        item['custodian_bank'] = values[5]
        item['revision_company'] = values[6]
        item['fiscal_year_end'] = values[7]
        item['swiss_representative'] = values[8]
        item['swiss_paying_agent'] = values[9]

        tax_status_table_parent = response.xpath('//div[@class="h5" and contains(text(), "Tax '
                                                 'Status")]/..')
        tax_status_table = tax_status_table_parent.xpath('table[1]/tbody')
        values = get_detail_table_values(tax_status_table, 3)
        item['switzerland'] = values[0]
        item['austria'] = values[1]
        item['uk'] = values[2]

        replication_table = tax_status_table_parent.xpath('table[2]/tbody')
        values = get_detail_table_values(replication_table, 5)
        item['indextype'] = values[0]
        item['swap_counterparty'] = values[1]
        item['collateral_manager'] = values[2]
        item['securities_lending'] = values[3]
        item['securities_lending_counterparty'] = values[4]

        yield item
