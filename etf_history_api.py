import eikon as ek
import logging
from datetime import date, datetime, timedelta
from eikon.data_grid import TR_Field
from typing import List

from db import Session, sql_engine
from db.models import EtfHistory, IsinCategory
from db.table_manager import create_table

# TODO: Include key in settings

ek.set_app_key('13977944d3544bdaac512a15754669286fecb2bb')


def extract_isins() -> List[str]:
    session = Session()
    isins_db = session.query(IsinCategory)

    isins = []
    for isin in isins_db:
        if not isin.etf_isin in isins:
            isins.append(isin.etf_isin)

    return isins


def get_skipped_isins() -> List[str]:
    isins = extract_isins()

    session = Session()
    for isin in session.query(EtfHistory.isin).distinct():
        isins.remove(isin._data[0])

    return isins


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


def get_timeseries():
    create_table(sql_engine)
    isins = extract_isins()

    for i in range(0, len(isins)):
        session = Session()

        try:
            ric = ek.get_data(isins[i], ['TR.LipperRICCode'])[0].values[0][1]
            if isinstance(ric, str):
                today = (date.today()).strftime('%Y-%m-%d')
                data = ek.get_timeseries(ric, fields=['TIMESTAMP', 'VALUE'], start_date='1990-01-01', end_date=today, interval='daily')
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
            session.rollback()
            logging.warning(f'No get_timeseries data available for ' + isins[i])

        session.close()


def get_data():
    create_table(sql_engine)
    isins = get_skipped_isins()

    for i in range(0, len(isins)):
        session = Session()

        try:
            today = date.today().strftime('%Y%m%d')
            data = ek.get_data(isins[i], ['TR.CLOSEPRICE.date', 'TR.CLOSEPRICE'], parameters={'SDate': '19900101', 'EDate': today, 'Frq': 'D'})
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
            session.rollback()
            logging.warning(f'No get_data values available for ' + isins[i])
    
        session.close()


if __name__ == '__main__':
    print('Getting etf history...')
    
    #get_timeseries()
    #get_data()
