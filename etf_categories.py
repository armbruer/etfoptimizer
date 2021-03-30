from sqlalchemy.orm import sessionmaker

from ETFOptimizer.spiders.extraetf_categories import url_to_asset, url_to_country, url_to_region, url_to_sector
from dbconnector import db_connect, create_table, EtfCategory

def save_categories():
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(EtfCategory) is not None:
        categories = [*url_to_asset.values()] + [*url_to_sector.values()] + [*url_to_region.values()] + [*url_to_country.values()]
        [session.add(EtfCategory(category=category)) for category in categories]

    session.commit()
    session.close()
