from setuptools import setup, find_packages

setup(
    name='etfoptimizer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=7.1.2,<7.2',
        'scrapy>=2.5.0,<2.6',
        'selenium>=3.141.0',
        'psycopg2>=2.8.6,<2.9',
        'SQLAlchemy>=1.4.9,<1.5',
        'sqlalchemy-utils>=0.37,<0.38',
        'pandas>=1.2.4,<1.3',
        'requests>=2.25.1,<2.26',
        'dash>=1.20.0,<1.21',
        'dash-bootstrap-components>=0.12.0,<0.13',
        'PyPortfolioOpt>=1.4.0,<1.5.0',
        'cvxopt>=1.2.0,<1.3',  # is a missing dependency for PyPortfolioOpt
        'scikit-learn>=0.24.0,<0.25.0',
        'numpy>=1.18.0,<1.21.0',
        'plotly>=4.14.0,<4.15.0',
        'openpyxl>=3.0.2,<3.1.0',
        'python-dateutil>=2.8.0,<2.9.0',
        'eikon>=1.1.0,<1.2'
    ],
    entry_points='''
        [console_scripts]
        etfopt=run:etfopt
    ''',
)
