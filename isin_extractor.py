import os

import pandas as pd
from openpyxl import load_workbook

from db import Session
from db.models import Etf


def extract_isins_from_db(out_file):
    """
    Retrieves all ISINs currently saved in database and writes them into an excel sheet
    """
    session = Session()
    df_isins = pd.read_sql(session.query(Etf).statement, session.bind)
    session.close()

    if os.path.isfile(out_file):
        book = load_workbook(out_file)
        # overwrite isins sheet if it already exists
        ws_rem = book.get_sheet_by_name('isins')
        if ws_rem is not None:
            book.remove_sheet(ws_rem)

        # keep existing content in other sheets
        writer = pd.ExcelWriter(out_file, engine='openpyxl')
        writer.book = book
    else:
        writer = pd.ExcelWriter(out_file, engine='openpyxl')

    df_isins.to_excel(writer, sheet_name='isins')
    writer.save()
    writer.close()
