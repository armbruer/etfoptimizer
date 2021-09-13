import configparser
import logging
import os
from pathlib import Path

# prevents config creation in frontend folder if app.py is used as entry point
config_file = Path(Path.cwd().parent, 'etfoptimizer.ini') if os.getcwd().find("frontend") != -1 else Path(
    'etfoptimizer.ini')

opt_entries = {'cutoff': '0.00001', 'rounding': '5', 'risk_free_rate': '0.02', 'total_portfolio_value': '100000'}
db_entries = {'dialect': 'postgresql', 'driver': 'psycopg2', 'username': '<username>',
              'password': '<password>', 'host': 'localhost', 'port': '5432', 'database': 'etf_optimization'}
hist_entries = {'app_key': '<key>'}
config_cache = {}


def create_if_not_exists():
    if os.path.isfile(config_file):
        logging.debug("EtfOptimizer config already exists")
        return

    # TODO does this work with setup.py?
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
    for k, v in hist_entries.items():
        db_section[k] = v

    with open(config_file, 'w+') as configfile:
        config.write(configfile)
        logging.info("Created initial config")


def read_config():
    if config_cache:
        logging.info("EtfOptimizer config already loaded")
        return

    config = configparser.ConfigParser()
    config.read(config_file)

    for k, v in db_entries.items():
        _add_to_cache(config, 'database-uri', k, v)

    for k, v in opt_entries.items():
        _add_to_cache(config, 'optimizer-defaults', k, v)

    for k, v in hist_entries.items():
        _add_to_cache(config, 'historic-data', k, v)

    logging.info("Loaded config successfully")


def _add_to_cache(config, sec, key, fallback):
    config_cache[f'{sec}.{key}'] = config[sec].get(key, fallback)


def get_value(section, key):
    return config_cache.get(f'{section}.{key}')


def get_sql_uri(nodriver=False):
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
