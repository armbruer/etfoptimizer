import logging
import time

import scrapy
from scrapy import Selector, Request
from selenium import webdriver

from ETFOptimizer.items import EtfCategoryItemLoader
from ETFOptimizer.spiders.common import handle_cookies_popup

url_to_asset = {
    2: "Aktien",
    3: "Anleihen",
    4: "Rohstoffe",
    1160: "Immobilien",
    5: "Geldmarkt",
    9: "Portfoliekonzepte",
    8: "Währungen"
}

url_to_region = {
    16: "Afrika",
    20: "Asien",
    1178: "Asien (ex Japan)",
    1206: "Asien-Pazifik",
    1177: "Asien-Pazifik (ex Japan)",
    1205: "BRIC",
    17: "Emerging Markets",
    15: "Europa",
    1179: "Europa (ex UK)",
    1180: "Eurozone",
    21: "Lateinamerika",
    14: "Nordamerika",
    18: "Osteuropa",
    1181: "Osteuropa (ex Russia)",
    1182: "Skandinavien",
    19: "Welt"
}

url_to_country = {
    48: "Australien",
    47: "Brasilien",
    45: "China",
    44: "Deutschland",
    43: "Frankreich",
    42: "Griechenland",
    41: "Großbritannien",
    40: "Indien",
    39: "Indonesien",
    38: "Italien",
    37: "Japan",
    36: "Kanada",
    35: "Korea",
    1225: "Kuwait",
    34: "Malaysia",
    33: "Mexiko",
    111: "Pakistan",
    110: "Philippinen",
    31: "Polen",
    30: "Portugal",
    29: "Russland",
    1124: "Saudi Arabien",
    1169: "Schweden",
    28: "Schweiz",
    108: "Singapur",
    27: "Spanien",
    26: "Südafrika",
    25: "Taiwan",
    24: "Thailand",
    23: "Türkei",
    22: "USA",
    49: "Vietnam",
    32: "Österreich"
}

url_to_sector = {
    1159: "Agrar",
    73: "Alternative Energien",
    54: "Automobil",
    55: "Banken",
    56: "Bau",
    1153: "Biotech",
    57: "Chemie",
    58: "Energie",
    59: "Finanzdienstleister",
    60: "Gesundheit",
    1158: "Goldminen",
    62: "Handel",
    61: "Haushaltsartikel",
    63: "Industriegüter",
    53: "Infrastruktur",
    93: "Konsumgüter",
    64: "Lebensmittel",
    309: "Luxus",
    65: "Medien",
    66: "Private Equity",
    67: "Reise & Freizeit",
    68: "Rohstoffe",
    72: "Sonstiges",
    51: "Technologie",
    69: "Telekommunikation",
    70: "Versicherungen",
    71: "Versorger",
    1163: "Wasser"
}

class ExtraetfSpider(scrapy.Spider):
    name = 'extraetf_categories'
    allowed_domains = ['extraetf.com']
    start_urls = ['https://de.extraetf.com/etf-search']
    base_url = 'https://de.extraetf.com'
    custom_settings = {
        'ITEM_PIPELINES': {
            'ETFOptimizer.pipelines.EtfCategoryPipeline': 300
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

        base_link = self.base_url + "?asset_class="
        for asset_id in url_to_asset.keys():
            link = base_link + str(asset_id)
            yield Request(link, callback=self.page_walk_run, cb_kwargs=dict(category=url_to_asset[asset_id],
                                                                            callback=self.parse_category))


        for asset_id in url_to_asset.keys():
            if asset_id == 2 or asset_id == 3 or asset_id == 1160:
                for region_id in url_to_region.keys():
                    link = base_link + str(asset_id) + "&region=" + str(region_id)
                    yield Request(link, callback=self.page_walk_run, cb_kwargs=dict(
                        subcategory=url_to_region[region_id], callback=self.parse_subcategory))

                for country_id in url_to_country.keys():
                    link = base_link + str(asset_id) + "&land=" + str(country_id)
                    yield Request(link, callback=self.page_walk_run, cb_kwargs=dict(
                        subcategory=url_to_country[country_id], callback=self.parse_subcategory))

                if asset_id == 2:
                    for sector_id in url_to_sector.keys():
                        link = base_link + str(asset_id) + "&sector=" + str(sector_id)
                        yield Request(link, callback=self.page_walk_run, cb_kwargs=dict(
                        subcategory=url_to_sector[sector_id], callback=self.parse_subcategory))


    def parse_category(self, response, category):
        isin = response.xpath('//div[@class="row etf-main-info mb-1"]/div[1]/text()').get()
        l = EtfCategoryItemLoader()
        l.add_value('isin', isin)
        l.add_value('category', category)
        yield l.load_item()

    def parse_subcategory(self, response, subcategory):
        isin = response.xpath('//div[@class="row etf-main-info mb-1"]/div[1]/text()').get()
        l = EtfCategoryItemLoader()
        l.add_value('isin', isin)
        l.add_value('subcategory', subcategory)
        yield l.load_item()


    def page_walk_run(self, response, category, callback):
        pagenum = 1
        while True:
            time.sleep(2.5)  # give enough time for updating contents inside selenium browser
            r = Selector(text=self.driver.page_source)
            for rel_link in r.xpath('//tbody/tr[@class="ng-star-inserted"]/td/div/div/a[@class="mr-1"]/@href').getall():
                link = self.base_url + rel_link
                logging.debug("Found link:" + link)

                # by handing the intended category to the callback responsible for handling individual items, we can
                # ensure each item gets the correct category
                yield Request(link, callback=callback, cb_kwargs=dict(category=category))

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
