import csv
import logging
import sys
from datetime import datetime

import pandas

from db import Session, sql_engine
from db.models import EtfHistory
from db.table_manager import create_table


def save_history_excel(historypath, isinpath):
    """
    Writes the retrieved ISIN and price data from the given files to database
    """
    create_table(sql_engine)
    session = Session()
    write_history_to_db(historypath, isinpath, session)
    session.close()


def write_history_to_db(historypath, isinpath, session):
    """
    Combines the retrieved ISIN and price data and writes it to the database
    """
    isin_dict = __get_isin_dict(isinpath)
    etf_history, header = __get_history_data(historypath)

    for i in range(0, len(etf_history)):
        datapoint_date = datetime.strptime(etf_history.iloc[i, 0], '%d.%m.%Y').date()

        for j in range(1, len(etf_history.columns), 3):
            isin = isin_dict[header[j]]
            price = float(etf_history.iloc[i, j])

            __write_history_value(datapoint_date, isin, price, session)


def __get_isin_dict(isinpath):
    """
    Reads the ISINs for which data is to be extracted from isinpath file
    """
    isin_dict = {}

    try:
        with open(isinpath, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')

            for row in csv_reader:
                isin_dict[row[1]] = row[0]
    except:
        print(f"File {isinpath} was not found at the given location.\n")
        sys.exit(1)

    return isin_dict


def __get_history_data(historypath):
    """
    Reads the extraxted price data from historypath file
    """
    try:
        etf_history = pandas.read_csv(historypath, sep=';')
        header = etf_history.columns.to_list()
    except:
        print(f"File {historypath} was not found at the given location.\n")
        sys.exit(1)
    return etf_history, header


def __write_history_value(datapoint_date, isin, price, session):
    """
    Write the extracted values to the database
    """
    try:
        res: EtfHistory = session.query(EtfHistory).filter_by(isin=isin, datapoint_date=datapoint_date).first()
        if res is not None:
            # allow re-imports of data, as nothing speaks against it, as this is useful in the following scenario:
            # refintiv has changed its history prices/revenue for some entries as they were wrong (very unlikely)
            # but this way we have also covered this scenario
            res.price = price

            logging.warning(f"Overwriting history for ETF '{isin}'. Did you re-import this data?")
        else:
            data = EtfHistory()

            data.isin = isin
            data.datapoint_date = datapoint_date

            data.price = price

            session.add(data)
            session.commit()
    except:
        logging.warning(f'Could not save data!')
        session.rollback()
        raise
