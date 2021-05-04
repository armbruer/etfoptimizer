from db import Base


def create_table(engine):
    """
    Creates the tables if they do not exist.
    """
    # unused models imports are required for sqlalchemy to create tables as expected
    Base.metadata.create_all(engine)


def drop_static_tables(engine):
    """
    Drops all tables with static data.
    """
    from db.models import Etf, EtfCategory, IsinCategory
    Base.metadata.drop_all(bind=engine, tables=[Etf.__table__, IsinCategory.__table__, EtfCategory.__table__])
