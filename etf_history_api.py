import eikon as ek
import logging
from datetime import date, datetime
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


def write_history_value(isin, date, price, session):
    try:
        res: EtfHistory = session.query(EtfHistory).filter_by(isin=isin, datapoint_date=date).first()
        if res is not None:
            # allow re-imports of data, as nothing speaks against it, as this is useful in the following scenario:
            # reuters has changed its history prices/revenue for some entries as they were wrong (very unlikely)
            # but this way we have also covered this scenario
            res.price = price

            logging.warning(f"Overwriting history for ETF '{isin}'. Did you re-import this data?")
        else:
            data = EtfHistory()

            data.isin = isin
            data.datapoint_date = date
            data.price = price

            session.add(data)
            session.commit()
    except:
        logging.warning(f'Could not save data!')
        session.rollback()
        raise


if __name__ == '__main__':
    create_table(sql_engine)
    session = Session()

    isins = extract_isins()
    for i in range(0, len(isins)):
        data = ek.get_data(isins[i], ['TR.CLOSEPRICE.date', 'TR.CLOSEPRICE'], parameters={'SDate': '20210201', 'EDate': '20210207', 'Frq': 'D'})
        for value in data[0].values:
            value_isin = value[0]
            value_date = datetime.strptime(value[1][0:10], '%Y-%m-%d').date()
            value_price = value[2]
            
            write_history_value(value_isin, value_date, value_price, session)
    
    session.close()
