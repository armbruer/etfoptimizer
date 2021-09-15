import configparser
import logging
import os
from appdirs import user_config_dir
from pathlib import Path

config_dir = Path(user_config_dir(appname="etfoptimizer"))
config_file = Path(config_dir, 'etfoptimizer.ini')

opt_entries = {'cutoff': '0.00001', 'rounding': '5', 'risk_free_rate': '0.02', 'total_portfolio_value': '100000'}
db_entries = {'dialect': 'postgresql', 'driver': 'psycopg2', 'username': '<username>',
              'password': '<password>', 'host': 'localhost', 'port': '5432', 'database': 'etf_optimization'}
hist_entries = {'app_key': '<key>'}
config_cache = {}


def create_if_not_exists():
    """
    Creates the config file if it does not already exist and populates the file with default values
    """

    config_dir.mkdir(parents=True, exist_ok=True)
    if os.path.isfile(config_file):
        logging.debug("EtfOptimizer config already exists")
        return

    config = configparser.ConfigParser()
    config.add_section('database-uri')
    db_section = config['database-uri']
    for k, v in db_entries.items():
        db_section[k] = v

    config.add_section('optimizer-defaults')
    opt_section = config['optimizer-defaults']
    config.set('optimizer-defaults', '; defaults are displayed when first opening the optimizer UI', '')
    for k, v in opt_entries.items():
        opt_section[k] = v

    config.add_section('historic-data')
    db_section = config['historic-data']
    config.set('historic-data', '; the Refinitiv API key used for retrieving historical price data', '')
    for k, v in hist_entries.items():
        db_section[k] = v

    with open(config_file, 'w+') as configfile:
        config.write(configfile)
        logging.info("Created initial config")


def read_config():
    """
    Reads all config entries and caches them.
    """
    if config_cache:
        logging.info("EtfOptimizer config already loaded")
        return

    config = configparser.ConfigParser()
    config.read(config_file)

    for k, v in db_entries.items():
        __add_to_cache(config, 'database-uri', k, v)

    for k, v in opt_entries.items():
        __add_to_cache(config, 'optimizer-defaults', k, v)

    for k, v in hist_entries.items():
        __add_to_cache(config, 'historic-data', k, v)

    logging.info("Loaded config successfully")


def get_value(section, key):
    """
    Retrieves a particular config value from cache at the given section and key
    """
    return config_cache.get(f'{section}.{key}')


def get_sql_uri(nodriver=False):
    """
    Returns the SQL URI string for connecting to the etf database.

    The nodriver option can be used to retrieve the SQL URI string without the driver string.
    """
    db_s = 'database-uri'
    dialect = get_value(db_s, 'dialect')
    driver = get_value(db_s, 'driver')
    user = get_value(db_s, 'username')
    pw = get_value(db_s, 'password')
    host = get_value(db_s, 'host')
    port = get_value(db_s, 'port')
    db = get_value(db_s, 'database')

    if nodriver:
        return f"{dialect}://{user}:{pw}@{host}:{port}/{db}"
    else:
        return f"{dialect}+{driver}://{user}:{pw}@{host}:{port}/{db}"


def __add_to_cache(config, sec, key, fallback):
    """
    Stores a config value in cache
    """
    config_cache[f'{sec}.{key}'] = config[sec].get(key, fallback)
