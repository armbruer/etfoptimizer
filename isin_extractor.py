from sqlalchemy.orm import sessionmaker
from dbconnector import db_connect, Etf
import csv
import logging


def extract_isins(out_file="isins.csv"):
    pre = "[ISIN Extractor]: "
    engine = db_connect()
    logging.info(pre + "Connected to database.")
    Session = sessionmaker(bind=engine)
    session = Session()

    isins = [etf.isin for etf in session.query(Etf)]
    logging.info(pre + "Retrieved ISINs from database.")
    session.close()

    with open(out_file, 'w', newline='') as isin_file:
        wr = csv.writer(isin_file, quoting=csv.QUOTE_ALL)
        for isin in isins:
            wr.writerow([isin])

    logging.info(pre + f"Wrote ISINS to {out_file}")
