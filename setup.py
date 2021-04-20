from setuptools import setup, find_packages

setup(
    name='etfoptimizer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires= [
        'Click',
        'scrapy',
        'selenium',
        'psycopg2',
        'SQLAlchemy',
        'pandas',
        'requests',
        'dash',
        'dash-bootstrap-components',
    ],
    entry_points='''
        [console_scripts]
        etfopt=run:cli
    ''',
)
