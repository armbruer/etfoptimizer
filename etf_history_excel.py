import csv
import logging
import sys
from datetime import datetime

import pandas

from db import Session, sql_engine
from db.models import EtfHistory
from db.table_manager import create_table


def save_history(historypath, isinpath):
    create_table(sql_engine)
    session = Session()
    write_history_to_db(historypath, isinpath, session)
    session.close()


def write_history_to_db(historypath, isinpath, session):
    isin_dict = __get_isin_dict(isinpath)
    etf_history, header = __get_history_data(historypath)

    for i in range(0, len(etf_history)):
        datapoint_date = datetime.strptime(etf_history.iloc[i, 0], '%d.%m.%Y').date()

        for j in range(1, len(etf_history.columns), 3):
            isin = isin_dict[header[j]]
            price = float(etf_history.iloc[i, j])
            price_index = float(etf_history.iloc[i, j + 1])
            return_index = float(etf_history.iloc[i, j + 2])

            __write_history_value(datapoint_date, isin, price, price_index, return_index, session)


def __get_isin_dict(isinpath):
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
    try:
        etf_history = pandas.read_csv(historypath, sep=';')
        header = etf_history.columns.to_list()
    except:
        print(f"File {historypath} was not found at the given location.\n")
        sys.exit(1)
    return etf_history, header


def __write_history_value(datapoint_date, isin, price, price_index, return_index, session):
    try:
        res: EtfHistory = session.query(EtfHistory).filter_by(isin=isin, datapoint_date=datapoint_date).first()
        if res is not None:
            # allow re-imports of data, as nothing speaks against it, as this is useful in the following scenario:
            # reuters has changed its history prices/revenue for some entries as they were wrong (very unlikely)
            # but this way we have also covered this scenario
            res.price = price
            res.price_index = price_index
            res.return_index = return_index

            logging.warning(f"Overwriting history for ETF '{isin}'. Did you re-import this data?")
        else:
            data = EtfHistory()

            data.isin = isin
            data.datapoint_date = datapoint_date

            data.price = price
            data.price_index = price_index
            data.return_index = return_index

            session.add(data)
            session.commit()
    except:
        logging.warning(f'Could not save data!')
        session.rollback()
        raise
