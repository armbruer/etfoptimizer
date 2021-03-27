import logging
import time

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from ETFOptimizer.items import EtfItemLoader, EtfItem
from ETFOptimizer.spiders.common import get_table_values, handle_cookies_popup


class ExtraetfSpider(scrapy.Spider):
    name = 'extraetf'
    allowed_domains = ['extraetf.com']
    start_urls = ['https://de.extraetf.com/etf-search']
    base_url = 'https://de.extraetf.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'ETFOptimizer.pipelines.EtfPipeline': 300
        }
    }

    def __init__(self, *a, **kw):
        """
        Creates a spider for crawling justetf.com website.
        Prepares a chrome driver for parsing items.
        """
        super().__init__(*a, **kw)

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        self.driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

    def parse(self, response, **kwargs):
        logging.info("Begin parsing ...")
        # load first page second time, this time through selenium
        self.driver.get(response.url)
        time.sleep(3)

        handle_cookies_popup(self.driver, '//a[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection"]')
        #self.increase_rows()

        pagenum = 1
        while True:
            time.sleep(2.5)  # give enough time for updating contents inside selenium browser
            r = Selector(text=self.driver.page_source)
            for rel_link in r.xpath('//tbody/tr[@class="ng-star-inserted"]/td/div/div/a[@class="mr-1"]/@href').getall():
                link = self.base_url + rel_link
                logging.debug("Found link:" + link)
                yield Request(link, callback=self.parse_item)

            logging.info(f"Extracted etfs from page {pagenum}")
            pagenum += 1
            next_page = self.driver.find_element_by_xpath('//a[@class="page-link"]')
            disabled = next_page.get_attribute('class').find('disabled')
            if not next_page.is_enabled() or not next_page.is_displayed() \
                    or disabled != -1:
                break

            # enable for debugging only
            if next_page != 1:
                break

            # a hacky fix for not being able to click on the next_page button
            # https://stackoverflow.com/questions/48665001/can-not-click-on-a-element-elementclickinterceptedexception-in-splinter-selen
            self.driver.execute_script("arguments[0].click();", next_page)

    def increase_rows(self):
        """
        Sets the number of rows (etfs) that are shown per page on justetf.com to 100.
        Using this method should increase performance, as fewer requests are needed.
        """
        # reduce the number of page loads required for better throughput, and fewer requests
        try:
            rows_select = Select(self.driver.find_element_by_xpath('//select[@id="select-page-limit"]'))
            logging.info("Row select:" + str(rows_select))
            rows_select.select_by_value("200 Zeilen ")
            time.sleep(1)
        except NoSuchElementException:
            logging.warning("Could not find page limit selector. Continuing ... ")

    def parse_item(self, response):
        """
        Parses the contents of a given webpage (response) into an EtfItem.
        """
        name = response.xpath('//div/h1[@class="mb-0 mr-0 mr-md-3"]/text()').get()
        logging.info(f"Parsing ETF '{name}'")

        isin_parent = response.xpath('//div[@class="row etf-main-info mb-1"]')
        isin = isin_parent.xpath('div[1]/text()').get()
        wkn = isin_parent.xpath('div[2]/text()').get()

        item = EtfItemLoader(item=EtfItem(), response=response)
        for field in item.item.fields:
            item.item.setdefault(field, None)

        item.add_value('name', name)
        item.add_value('isin', isin)
        item.add_value('wkn', wkn)

        # main_data table
        main_parent = response.xpath('//tbody/tr/td[contains(text(), "(TER)")]/../..')
        values = get_table_values(main_parent, 10, '/td[2]/text()')
        item.add_value('ter', values[0])
        item.add_value('replication', values[1])  # TODO MERGE VALUES todo ADD abbildungsart
        item.add_value('distribution_policy', values[3])
        item.add_value('fund_size', values[4])
        item.add_value('inception', values[5])  # TODO CONVERSION
        item.add_value('fund_currency', values[6])

        more_details_link = response.xpath('//a[contains(text(), "Mehr Details")]/@href').get()
        link = self.base_url + more_details_link
        yield Request(link, callback=self.parse_item_details, cb_kwargs=dict(item=item))

    def parse_item_details(self, response, item):

        legal_structure_parent = response.xpath('//tbody/tr/td[contains(text(), "Anbieter")]/../..')
        values = get_table_values(legal_structure_parent, 8, '/td[2]/text()')

        item.add_value('fund_provider', values[0])
        item.add_value('legal_structure', values[1])
        item.add_value('fund_domicile', values[2])
        item.add_value('fund_structure', values[3])
        item.add_value('ucits_compliance', values[4])  # todo convert yes/no to boolean
        item.add_value('administrator', values[5])
        item.add_value('revision_company', values[6])
        item.add_value('custodian_bank', values[7])

        tax_parent = response.xpath('//tbody/tr/td[contains(text(), "Deutschland")]/../..')
        values = get_table_values(tax_parent, 4, '/td[2]/text()')

        # TODO fund_size in million euros?
        # todo TAX_GERMANY?
        item.add_value('tax_switzerland', values[1])
        item.add_value('tax_austria', values[2])
        item.add_value('tax_uk', values[3])
        item.add_value('tax_data', response.xpath('//tbody/tr/td[contains(text(), "Steuerdaten")]/../td[2]/a/@href').get())


        # TODO MISSING VALUES
        #benchmark_index = response.xpath('//p/a[@class="label label-default labelwrap"]/text()').get()
        #l.add_value('benchmark_index', benchmark_index)
        #item.add_value('investment_advisor', values[6])
        #item.add_value('strategy_risk', values[2])
        #item.add_value('volatility_one_year', values[0])
        #item.add_value('currency_risk', values[4])
        #item.add_value('distribution_frequency', values[1])
        #item.add_value('fiscal_year_end', values[7])
        #item.add_value('swiss_representative', values[8])
        #item.add_value('swiss_paying_agent', values[9])
        #item.add_value('indextype', values[0])
        #item.add_value('swap_counterparty', values[1])
        #item.add_value('collateral_manager', values[2])
        #item.add_value('securities_lending', values[3])
        #item.add_value('securities_lending_counterparty', values[4])

        yield item.load_item()

