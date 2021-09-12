import logging
from datetime import date, datetime
from typing import List

import eikon as ek

import config
from db import Session, sql_engine
from db.models import EtfHistory, IsinCategory
from db.table_manager import create_table


def get_isins() -> List[str]:
    session = Session()
    isins_db = session.query(IsinCategory)

    isins = []
    for isin in isins_db:
        if not isin.etf_isin in isins:
            isins.append(isin.etf_isin)

    return isins


# Identifies the ISINs for which no data is available with the get_timeseries function
def get_skipped_isins() -> List[str]:
    isins = get_isins()

    session = Session()
    for isin in session.query(EtfHistory.isin).distinct():
        isins.remove(isin._data[0])

    return isins


# Sets the start date to 01.01.1990 or the most recent date for which data has already been extracted
def get_latest_date():
    start_date = date(1990, 1, 1)

    session = Session()
    for datapoint_date in session.query(EtfHistory.datapoint_date).distinct():
        if start_date < datapoint_date._data[0]:
            start_date = datapoint_date._data[0]

    return str(start_date)


# Write the extracted values to the database
def write_history_value(isin, date, price, session):
    try:
        res: EtfHistory = session.query(EtfHistory).filter_by(isin=isin, datapoint_date=date).first()
        if res is None:
            data = EtfHistory()

            data.isin = isin
            data.datapoint_date = date
            data.price = price

            session.add(data)
            session.commit()
    except:
        logging.warning(f'Could not save data')
        session.rollback()
        raise


# Extracts historic price data with the get_timeseries function
# The extracted data consists of timestamps and prices for all available ISINs from the start date to today
def get_timeseries(start_date):
    _set_app_key()
    create_table(sql_engine)
    isins = get_isins()

    for i in range(0, len(isins)):
        session = Session()

        try:
            ric = ek.get_data(isins[i], ['TR.LipperRICCode'])[0].values[0][1]
            if isinstance(ric, str):
                today = (date.today()).strftime('%Y-%m-%d')
                data = ek.get_timeseries(ric, fields=['TIMESTAMP', 'VALUE'], start_date=start_date, end_date=today, interval='daily')
                for j in range(0, len(data.values)):
                    isin = isins[i]
                    datapoint_date = data.axes[0][j].date()
                    price = data.values[j][0]
                    write_history_value(isin, datapoint_date, price, session)

                print('Finished writing get_data values for ' + isins[i])
            else:
                logging.warning(f'No get_timeseries data available for ' + isins[i])

        except KeyboardInterrupt:
            session.rollback()
            exit(0)
        except:
            # For some ISINs no data is available with the get_timeseries function
            session.rollback()
            logging.warning(f'No get_timeseries data available for ' + isins[i])

        session.close()


# Extracts historic price data with the get_data function
# The extracted data consists of timestamps and prices for all available ISINs from the start date to today
def get_data(start_date):
    _set_app_key()
    create_table(sql_engine)
    isins = get_skipped_isins()

    for i in range(0, len(isins)):
        session = Session()

        try:
            today = date.today().strftime('%Y%m%d')
            data = ek.get_data(isins[i], ['TR.CLOSEPRICE.date', 'TR.CLOSEPRICE'], parameters={'SDate': start_date, 'EDate': today, 'Frq': 'D'})
            for value in data[0].values:
                insert = True
                if isinstance(value[2], float):
                    isin = isins[i]
                    datapoint_date = datetime.strptime(value[1][0:10], '%Y-%m-%d').date()
                    price = value[2]
                else:
                    insert = False

                if insert:
                    write_history_value(isin, datapoint_date, price, session)

            print('Finished writing get_data values for ' + isins[i])

        except KeyboardInterrupt:
            session.rollback()
            exit(0)
        except:
            # For some ISINs no data is available with the get_data function
            session.rollback()
            logging.warning(f'No get_data values available for ' + isins[i])

        session.close()


def save_history_api():
    print('Getting etf history...')

    start_date = get_latest_date()
    get_timeseries(start_date)
    get_data(start_date.replace('-', ''))


def _set_app_key():
    ek.set_app_key(config.get_value('historic-data', 'app_key'))
