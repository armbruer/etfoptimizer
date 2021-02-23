import dbconnector

if __name__ == '__main__':
    connector = dbconnector.DbConnector()
    conn = connector.connect(dbconnector.config())
    print(conn)
    connector.close()
