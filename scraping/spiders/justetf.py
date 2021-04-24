import logging
import time

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from scraping.items import EtfItem, EtfItemLoader


class JustetfSpider(scrapy.Spider):
    name = 'justetf'
    allowed_domains = ['justetf.com']
    start_urls = ['https://justetf.com/de/find-etf.html']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scraping.pipelines.EtfPipeline': 300
        },
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, *a, **kw):
        """
        Creates a spider for crawling justetf.com website.
        Prepares a chrome driver for parsing items.
        """
        super().__init__(*a, **kw)

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        self.driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

    def parse(self, response, **kwargs):
        logging.info("Begin parsing ...")
        # load first page second time, this time through selenium
        self.driver.get(response.url)
        time.sleep(3)

        self.handle_cookies_popup('//a[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection"]')

        pagenum = 1
        while True:
            time.sleep(2.5)  # give enough time for updating contents inside selenium browser
            r = Selector(text=self.driver.page_source)
            for link in r.xpath('//tbody/tr[@role="row"]/td/a[@class="link"]/@href').getall():
                logging.debug("Found link:" + link)
                yield Request(link, callback=self.parse_item)

            logging.info(f"Extracted etfs from page {pagenum}")
            pagenum += 1
            next_page = self.driver.find_element_by_xpath('//a[@id="etfsTable_next"]')
            disabled = next_page.get_attribute('class').find('disabled')
            if not next_page.is_enabled() or not next_page.is_displayed() \
                    or disabled != -1:
                break

            # enable for debugging only
            # if next_page != 1:
            #     break

            # a hacky fix for not being able to click on the next_page button
            # https://stackoverflow.com/questions/48665001/can-not-click-on-a-element-elementclickinterceptedexception-in-splinter-selen
            self.driver.execute_script("arguments[0].click();", next_page)

    @staticmethod
    def get_table_values(selector, table_size, path):
        """
        Get the text contents of a table given the selector, table_size and an path.
        """
        # xpath counting starts with one :/
        values = [selector.xpath('*[' + str(i) + ']' + path).get() for i in range(1, table_size + 1)]
        return values


    def handle_cookies_popup(self, accept_xpath):
        """
        Clicks on 'Allow Selection' in the cookie selection popup when entering the website.
        """
        try:
            # cookie settings: allow selection
            allow_selection_button = self.driver.find_element_by_xpath(accept_xpath)
            allow_selection_button.click()
            time.sleep(0.5)
        except NoSuchElementException:
            logging.warning("No cookie message was found. Continuing ...")

    def parse_item(self, response):
        """
        Parses the contents of a given webpage (response) into an EtfItem.
        """
        isin_parent = response.xpath('//span[@class="vallabel" and .="ISIN"]/..')
        name = isin_parent.xpath('../*[1]/text()').getall()
        logging.info(f"Parsing ETF '{name}'")

        isin = isin_parent.xpath('*[2]/text()').getall()
        wkn = isin_parent.xpath('*[4]/text()').getall()

        l = EtfItemLoader(item=EtfItem(), response=response)
        for field in l.item.fields:
            l.item.setdefault(field, None)

        l.add_value('name', name)
        l.add_value('isin', isin)
        l.add_value('wkn', wkn)

        benchmark_index = response.xpath('//p/a[@class="label label-default labelwrap"]/text()').get()
        l.add_value('benchmark_index', benchmark_index)

        ter = response.xpath('//div[@class="h5" and contains(text(), "Fees")]/../div[2]/div/div[1]/div[1]/text()').get()
        l.add_value('ter', ter)

        risk_parent = response.xpath('//div[@class="h5" and contains(text(), "Risk")]/..')

        l.add_value('fund_size', risk_parent.xpath('div[2]/div/div[1]/div[1]/text()').get())
        risk_table = risk_parent.xpath('table/tbody')
        values = self.get_table_values(risk_table, 7, '/td[2]/text()')
        l.add_value('replication', risk_table.xpath('*[1]/td[2]/span[1]/text()').get())
        l.add_value('legal_structure', values[1])
        l.add_value('strategy_risk', values[2])
        l.add_value('fund_currency', values[3])
        l.add_value('currency_risk', values[4])
        l.add_value('volatility_one_year', risk_table.xpath('*[6]/td[2]/span[1]/text()').get())
        l.add_value('inception', values[6])

        dividend_table = response.xpath('//div[@class="h5 margin-lineup" and contains(text(), "Dividend/ '
                                        'Taxes")]/../table/tbody')
        values = self.get_table_values(dividend_table, 4, '/td[2]/text()')
        l.add_value('distribution_policy', values[0])
        l.add_value('distribution_frequency', values[1])
        l.add_value('fund_domicile', values[2])
        l.add_value('tax_data', dividend_table.xpath('*[4]/td[2]/a/@href').get())

        legal_structure_table = response.xpath('//div[@class="h5" and contains(text(), "Legal '
                                               'structure")]/../table/tbody')
        values = self.get_table_values(legal_structure_table, 10, '/td[2]/text()')
        l.add_value('fund_structure', values[0])
        l.add_value('ucits_compliance', values[1])
        l.add_value('fund_provider', values[2])
        l.add_value('administrator', values[3])
        l.add_value('investment_advisor', values[4])
        l.add_value('custodian_bank', values[5])
        l.add_value('revision_company', values[6])
        l.add_value('fiscal_year_end', values[7])
        l.add_value('swiss_representative', values[8])
        l.add_value('swiss_paying_agent', values[9])

        tax_status_table = response.xpath('//td[contains(text(), "Switzerland")]/../..')
        values = self.get_table_values(tax_status_table, 3, path='/td[2]/span/text()')
        l.add_value('tax_switzerland', values[0])
        l.add_value('tax_austria', values[1])
        l.add_value('tax_uk', values[2])

        replication_table = response.xpath('//td[contains(text(), "Indextype")]/../..', )
        values = self.get_table_values(replication_table, 5, path='/td[2]/span/text()')
        l.add_value('indextype', values[0])
        l.add_value('swap_counterparty', values[1])
        l.add_value('collateral_manager', values[2])
        l.add_value('securities_lending', values[3])
        l.add_value('securities_lending_counterparty', values[4])

        return l.load_item()
