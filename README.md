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
* A local or remote database that is [compatible](https://www.sqlalchemy.org/features.html) with *SQLAlchemy*. 
    *PostgreSQL* is strongly recommended as it is the only one tested.
    * Arch Linux [setup guide](https://wiki.archlinux.org/index.php/PostgreSQL) (most steps should also be applicable to other `systemd` based distributions)
    * In Fedora there is one quirk: make sure you change `pg_hba.conf` as described in this [answer](https://support.plesk.com/hc/en-us/articles/360024041714-Unable-to-change-PostgreSQL-admin-password-or-log-in-to-PostgreSQL-on-Plesk-psql-FATAL-Ident-authentication-failed-for-user-postgres-)
    * Windows [setup guide](https://www.postgresqltutorial.com/install-postgresql/)
* On Linux: Ensure you have installed `de_DE` and `en_US` languages. 
  Not sure yet if and what is required on Windows.
  
Installation
============

1. Clone the repository: `git clone https://gitlab.lrz.de/armbruer/etfoptimizer.git`
2. Setting up a virtual environment, either with [venv](https://docs.python.org/3/library/venv.html) 
   or [conda](https://docs.conda.io/en/latest/miniconda.html) is recommended to avoid package version clashes with other projects in the future.
3. a) On Linux: 
    * Change directory into project folder: `cd etfoptimizer`
    * Install with `pip3 install .`
3. b) TODO Ruben    
    
Post-Installation Setup
=======================
1. Make sure you have installed all dependencies, downloaded the repository and installed its python dependencies.
2. Create a new database, e.g. for Linux and PostgreSQL:
    1. Log in as `postgres` user (default user) by running `su` and `su -l postgres`
    2. Run `createdb <database name>` to create the database
3. The database connection:
   Either navigate from the project working directory to `ÈTFOptimizer/settings.py` and change the `SQL_URI` parameter.
   The required format for this step is: `SQL_URI = 'postgresql+psycopg2://<user>:<password>:<port>/<database name>'`.
   
   Or run directly `python3 run_crawlers.py setupdb` which will guide you though the database connection setup.

Data retrieval
==============

This project distinguishes for the ETF data into two classes, the first one being the `static data class`, which never changes 
(or at least only very rarely) and the second one being the `dynamic data class`, which contains the daily/monthly prices 
and other dynamic data of the ETFs.

First, you need to retrive the static data. For this, we strongly recommend running our interactive crawler by typing
`python3 run_crawlers.py runi`. Please note, this will ask you whether you want to delete all static data. 
Deleting the static data is only required if you wish to rerun crawlers, as mentioned previously some static data might 
prone to change over long times. Deleting does not hurt, if you run this for the first time, as no previous data is available. 
Please answer each question with `y` in order to download all static data. This might take up to 15 minutes.

TODO second step Ruben
    
