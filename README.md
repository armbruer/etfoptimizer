Supported Platforms
===================
Windows & Linux

Dependencies
============
* Python 3: Ensure it is installed in your `PATH` environment variable. To check run `python --version` from your
  Terminal (Linux), or from your Power Shell (Windows). We have tested only with versions 3.9 and above. In case you
  want to use an older version, no guarantees can be made.
* C++ Build Tools (required for the [solver](https://www.cvxpy.org/) used by
  the [portfolio optimization library](https://github.com/robertmartin8/PyPortfolioOpt)):
    * Linux: your distribution should have a working C++ toolchain per default installed
    * Windows: [download](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16)
      the visual studio build tools and follow the
      [install instructions](https://drive.google.com/file/d/0B4GsMXCRaSSIOWpYQkstajlYZ0tPVkNQSElmTWh1dXFaYkJr/view))
* Chrome Driver (required due to `selenium`)
    * Chrome might be sufficient, depending on your OS
    * Ensure it is installed in your `PATH` environment variable
    * Other drivers (Firefox, ...) are not yet supported
    * [Driver installation details](https://selenium-python.readthedocs.io/installation.html)
* A local or remote database that is [compatible](https://www.sqlalchemy.org/features.html) with *SQLAlchemy*.
  *PostgreSQL* is strongly recommended as it is the only one tested.
    * Arch Linux [setup guide](https://wiki.archlinux.org/index.php/PostgreSQL) (most steps should also be applicable to
      other `systemd` based distributions)
    * In Fedora there is one quirk: make sure you change `pg_hba.conf` as described in
      this [answer](https://support.plesk.com/hc/en-us/articles/360024041714-Unable-to-change-PostgreSQL-admin-password-or-log-in-to-PostgreSQL-on-Plesk-psql-FATAL-Ident-authentication-failed-for-user-postgres-)
    * Windows [setup guide](https://www.postgresqltutorial.com/install-postgresql/)
* Refinitiv Workspace (required for the dynamic data)
  You need to be logged in with your Refinitiv account in order to retrieve the data.
    * Windows: [download](https://www.refinitiv.com/en/products/refinitiv-workspace/download-workspace)
* On Linux: Ensure you have installed `de_DE` and `en_US` languages. 
  Not sure yet if and what is required on Windows.
  
Developer Installation
======================

1. Clone the repository: `git clone https://gitlab.lrz.de/armbruer/etfoptimizer.git`
2. a) On Linux Distributions:
    * Change directory into project folder: `cd etfoptimizer`
    * Set up a [virtual environment](https://docs.python.org/3/library/venv.html) with 
      `python3 -m venv venv && source ./venv/bin/activate` and run `python3 -m pip install -U pip wheel setuptools`
    * Always activate your virtual environment first (with `source ./venv/bin/activate`) then you can install
      the command line tool (including the changes you made) using `pip install --editable=.`
    * Now check if your installation succeeded by running `etfopt`. The output should show the help page of this tool.
2. b) On Windows:
    * Change directory into project folder: `cd etfoptimizer`
    * Set up a [virtual environment](https://docs.python.org/3/library/venv.html) with 
      `python3 -m venv venv && venv\Scripts\activate.bat` and run `python3 -m pip install -U pip wheel setuptools`
    * Always activate your virtual environment first (with `venv\Scripts\activate.bat`) then you can install
      the command line tool (including the changes you made) using `pip install --editable=.`
    * Now check if your installation succeeded by running `etfopt`. The output should show the help page of this tool.  

User Installation
=================

1. Install the wheel package: `pip install wheel --user`.
2. Download a packaged version of `etfoptimizer` from tbd.
3. Install `etfoptimizer` using `pip install <download location> --user`

    
Post-Installation Setup (Required for Users and Developers)
===========================================================
1. Make sure you have installed all dependencies, downloaded the repository and installed its python dependencies.
2. Create a new database, e.g. for Linux and PostgreSQL:
    1. Log in as `postgres` user (default user) by running `su` and `su -l postgres`
    2. Run `createdb <database name>` to create the database
3. The database connection:
   Either navigate from the project working directory to `ÈTFOptimizer/settings.py` and change the `SQL_URI` parameter.
   The required format for this step is: `SQL_URI = 'postgresql+psycopg2://<user>:<password>:<port>/<database name>'`.

   Or run directly `python3 run_crawlers.py setupdb` which will guide you though the database connection setup.
4. Log in the Refinitiv Workspace and create an app key for the Eikon API. (A guide for this can be found at
   https://developers.refinitiv.com/en/api-catalog/eikon/eikon-data-api/quick-start). Afterwards add the key to the 
   `app_key` variable in `etfoptimizer.ini`. 

Data retrieval
==============

This project distinguishes for the ETF data into two classes, the first one being the `static data class`, which never changes 
(or at least only very rarely) and the second one being the `dynamic data class`, which contains the daily/monthly prices 
and other dynamic data of the ETFs.

First, you need to retrieve the static data. For this, we strongly recommend running our interactive crawler by typing
`python3 run_crawlers.py runi`. Please note, this will ask you whether you want to delete all static data. 
Deleting the static data is only required if you wish to rerun crawlers, as mentioned previously some static data might 
prone to change over long times. Deleting does not hurt, if you run this for the first time, as no previous data is available. 
Please answer each question with `y` in order to download all static data. This might take up to 15 minutes.

The dynamic data can be retrieved by typing `python3 run.py import-history`. This will automatically write all available dynamic
data to the database. In case this command has already been run, the new data will be added to the already existing data. 

Packaging Instructions
======================

1. Activate your virtual environment `source ./venv/bin/activate`.
2. Package the project `python setup.py bdist_wheel`.
3. Upload to TDB.
