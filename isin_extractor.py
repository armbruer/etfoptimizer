#!/usr/bin/python3

# Isin Extractor is a small, static script for extracting only ISINs
# from the database into the first column of a .csv file. Please run
# this script ONLY after the database table etfs has been created.

from sqlalchemy.orm import sessionmaker
from dbconnector import db_connect, JustetfItem
import csv
import logging

pre = "[ISIN Extractor]: "
engine = db_connect()
logging.info(pre + "Connected to database.")
Session = sessionmaker(bind=engine)
session = Session()

isins = [etf.isin for etf in session.query(JustetfItem)]
logging.info(pre + "Retrieved ISINs from database.")
session.close()

with open("isins.csv", 'w', newline='') as isin_file:
    wr = csv.writer(isin_file, quoting=csv.QUOTE_ALL)
    for isin in isins:
        wr.writerow([isin])

logging.info(pre + "Wrote ISINS to isins.csv")
