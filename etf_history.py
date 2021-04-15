import csv
import logging
import os
import pandas

from datetime import datetime
from db.dbconnector import create_table, db_connect
from db.models import EtfHistory
from sqlalchemy.orm import sessionmaker


def get_isin_dict():  # todo file parameter
    isin_dict = {}

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'isin.csv'), 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')

        for row in csv_reader:
            isin_dict[row[1]] = row[0]

    return isin_dict


def get_etf_history(session):  # todo file parameter
    isin_dict = get_isin_dict()

    etf_history = pandas.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'etf_history.csv'), sep = ';')
    header = etf_history.columns.to_list()

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


def create_database():
    engine = db_connect()
    create_table(engine)

    Session = sessionmaker(engine)
    session = Session()

    get_etf_history(session)

    session.close()


create_database() # Add to run_crawlers.py
