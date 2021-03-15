Supported Platforms
===================
Windows & Linux, other platforms are untested

Dependendencies
===============
* Python 3
* Chrome Driver (required due to selenium)
    * Chrome might be sufficient, depending on your OS
    * Ensure it is installed in your `PATH` environment variable  
    * Other drivers (Firefox, ...) are not yet supported
    * [Driver installation details](https://selenium-python.readthedocs.io/installation.html)
* A local or remote database that is [compatible](https://www.sqlalchemy.org/features.html) with sqlalchemy. 
    *PostgreSQL* is strongly recommended as it is the only one tested.
    * Arch Linux [setup guide](https://wiki.archlinux.org/index.php/PostgreSQL) (most steps should also be applicable to other `systemd` based distributions)
    * Windows [setup guide](https://www.postgresqltutorial.com/install-postgresql/)
* Python packages:
    * ```pip install selenium```
    * ```pip install scrapy```
    * ```pip install sqlalchemy```
    * ```pip install psycopg2```
    
Setup
=====
1. Make sure you have installed all dependencies.
2. Create a new database, e.g. for Linux and PostgreSQL:
    1. Log in as `postgres` user (default user) by running `su` and `su -l postgres`
    2. Run `createdb <database name>` to create the database
3. In `settings.py` adapt the parameter `SQL_URI` to your database configuration. The required format is
`SQL_URI = 'postgresql+psycopg2://<user>:<password>:<port>/<database name>'`.
4. To crawl the justetf.com webpage run `scrapy crawl justetf`. 
    
