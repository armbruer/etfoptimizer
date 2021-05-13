import eikon as ek
from typing import List

from eikon.data_grid import TR_Field

from db import Session
from db.models import IsinCategory

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


if __name__ == '__main__':
    #isins = extract_isins()
    isins = ['DE0002635265', 'DE0006289465', 'DE000A0F5UK5', 'XS2115336336']

    data_get_data = ek.get_data(isins, 'TR.PRICE', parameters={'SDate': '20210201', 'EDate': '20210207', 'Frq': 'D'})
    print(data_get_data)

    print('\n----------------------------------------------------------------------------------------------------\n')

    data_get_data = ek.get_data(isins, 'TR.MIDPRICE', parameters={'SDate': '20210201', 'EDate': '20210207', 'Frq': 'D'})
    print(data_get_data)

    print('\n----------------------------------------------------------------------------------------------------\n')

    rics = ek.get_symbology(isins, from_symbol_type= 'ISIN',to_symbol_type='RIC')
    print(rics)

    print('\n----------------------------------------------------------------------------------------------------\n')

    #data_get_timeseries = ek .get_timeseries(rics, fields=['VALUE', 'HIGH', 'LOW'], start_date='2021-02-01', end_date='2021-02-07')
    #print(data_get_timeseries)