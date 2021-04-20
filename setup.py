from setuptools import setup, find_packages

setup(
    name='etfoptimizer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires= [
        'Click>=7.1.2',
        'scrapy>=2.5.0',
        'selenium>=3.141.0',
        'psycopg2>=2.8.6',
        'SQLAlchemy>=1.4.9',
        'pandas>=1.2.4',
        'requests>=2.25.1',
        'dash>=1.20.0',
        'dash-bootstrap-components>=0.12.0',
    ],
    entry_points='''
        [console_scripts]
        etfopt=run:cli
    ''',
)
