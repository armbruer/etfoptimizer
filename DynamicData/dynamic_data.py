import csv
import logging
import os
import pandas

from datetime import date, datetime
from sqlalchemy import Column, Date, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()


class DynamicData(Base):
    __tablename__ = 'dynamic data'

    isin = Column(String, primary_key=True)
    datapoint_date = Column(Date, primary_key=True)

    price = Column(Float)
    price_index = Column(Float)
    return_index = Column(Float)


def get_isin_dict():
    isin_dict = {}

    with open(os.path.dirname(os.path.realpath(__file__)) + '\\isin_test.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        header = next(csv_reader)

        for row in csv_reader:
            isin_dict[row[1]] = row[0]

    return isin_dict


def get_dynamic_data(session):
    isin_dict = get_isin_dict()
    
    dynamic_data = pandas.read_csv(os.path.dirname(os.path.realpath(__file__)) + '\\dynamic_data_test.csv', sep = ';')
    header = dynamic_data.columns.to_list()

    isin = ''

    price = 0.0
    price_index = 0.0
    return_index = 0.0

    for i in range(0, len(dynamic_data)):
        date = datetime.strptime(dynamic_data.iloc[i, 0], '%d.%m.%Y').date()

        for j in range(1, len(dynamic_data.columns)):
            if j % 3 == 1:
                isin = isin_dict[header[j]]
                price = float(dynamic_data.iloc[i, j])
            elif j % 3 == 2:
                price_index = float(dynamic_data.iloc[i, j])
            else:
                return_index = float(dynamic_data.iloc[i, j])

                try:
                    database_data = self.session.query(DynamicData)
                    exists = database_data.filter_by(isin=data.isin, datapoint_date=data.datapoint_date).first() is not None
                    if exists:
                        logging.warning(f'Updated values are not reflected in database.')
                    else:
                        data = DynamicData()

                        data.isin = isin
                        data.datapoint_date = date

                        data.price = price
                        data.price_index = price_index
                        data.return_index = return_index

                        session.add(data)
                        session.commit()
                except:
                    logging.warning(f'Could not save data!')
                    self.session.rollback()
                    raise


def create_database():
    engine = create_engine('postgresql+psycopg2://postgres:poIDPst42!gre@localhost:5432/ETFData')
    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)
    session = Session()

    get_dynamic_data(session)

    session.close()


create_database()
