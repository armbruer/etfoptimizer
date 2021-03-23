import time
import logging

from selenium.common.exceptions import NoSuchElementException


def get_table_values(selector, table_size, path):
    """
    Get the text contents of a table given the selector, table_size and an path.
    """
    # xpath counting starts with one :/
    values = [selector.xpath('*[' + str(i) + ']' + path).get() for i in range(1, table_size + 1)]
    return values


def handle_cookies_popup(driver, accept_xpath):
    """
    Clicks on 'Allow Selection' in the cookie selection popup when entering the website.
    """
    try:
        # cookie settings: allow selection
        allow_selection_button = driver.find_element_by_xpath(accept_xpath)
        allow_selection_button.click()
        time.sleep(0.5)
    except NoSuchElementException:
        logging.warning("No cookie message was found. Continuing ...")
