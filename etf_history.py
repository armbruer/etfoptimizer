import csv
import logging
import os
import pandas
import sys

from datetime import datetime
from db.dbconnector import create_table, db_connect
from sqlalchemy.orm import sessionmaker

from db.dbmodels import EtfHistory


def get_isin_dict(path):
    isin_dict = {}

    try:
        with open(os.path.join(path, 'isin.csv'), 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')

            for row in csv_reader:
                isin_dict[row[1]] = row[0]
    except:
        print("File isin.csv was not found at the given location.\n")
        sys.exit(1)

    return isin_dict


def get_etf_history(path, session):
    isin_dict = get_isin_dict(path)

    try:
        etf_history = pandas.read_csv(os.path.join(path, 'etf_history.csv'), sep = ';')
        header = etf_history.columns.to_list()
    except:
        print("File etf_history.csv was not found at the given location.\n")
        sys.exit(1)

    isin = ''

    price = 0.0
    price_index = 0.0
    return_index = 0.0

    for i in range(0, len(etf_history)):
        datapoint_date = datetime.strptime(etf_history.iloc[i, 0], '%d.%m.%Y').date()

        for j in range(1, len(etf_history.columns)):
            if j % 3 == 1:
                isin = isin_dict[header[j]]
                price = float(etf_history.iloc[i, j])
            elif j % 3 == 2:
                price_index = float(etf_history.iloc[i, j])
            else:
                return_index = float(etf_history.iloc[i, j])

                try:
                    database_data = session.query(EtfHistory)
                    exists = database_data.filter_by(isin=isin, datapoint_date=datapoint_date).first() is not None
                    if exists:
                        logging.warning(f'Updated values are not reflected in database.')
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


def save_history(path):
    engine = db_connect()
    create_table(engine)

    Session = sessionmaker(engine)
    session = Session()

    get_etf_history(path, session)

    session.close()
