Supported Platforms
===================
Windows & Linux, other platforms are untested

Dependencies
============
* Python 3
* Chrome Driver (required due to selenium)
    * Chrome might be sufficient, depending on your OS
    * Ensure it is installed in your `PATH` environment variable  
    * Other drivers (Firefox, ...) are not yet supported
    * [Driver installation details](https://selenium-python.readthedocs.io/installation.html)
* A local or remote database that is [compatible](https://www.sqlalchemy.org/features.html) with sqlalchemy. 
    *PostgreSQL* is strongly recommended as it is the only one tested.
    * Arch Linux [setup guide](https://wiki.archlinux.org/index.php/PostgreSQL) (most steps should also be applicable to other `systemd` based distributions)
    * In Fedora there is one quirk: make sure you change `pg_hba.conf` as described in this [answer](https://support.plesk.com/hc/en-us/articles/360024041714-Unable-to-change-PostgreSQL-admin-password-or-log-in-to-PostgreSQL-on-Plesk-psql-FATAL-Ident-authentication-failed-for-user-postgres-)
    * Windows [setup guide](https://www.postgresqltutorial.com/install-postgresql/)
* Python packages: 
    * selenium, scrapy, sqlalchemy
    * Use `pip install -r requirements.txt` to install correct versions
    
Setup
=====
1. Make sure you have installed all dependencies.
2. Create a new database, e.g. for Linux and PostgreSQL:
    1. Log in as `postgres` user (default user) by running `su` and `su -l postgres`
    2. Run `createdb <database name>` to create the database
3. In `settings.py` adapt the parameter `SQL_URI` to your database configuration. The required format is
`SQL_URI = 'postgresql+psycopg2://<user>:<password>:<port>/<database name>'`.
4. To crawl the justetf.com webpage run `scrapy crawl justetf`. 
    
