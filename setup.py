from setuptools import setup, find_packages

setup(
    name='etfoptimizer',
    version='0.1.0',
    description="EtfOptimizer is a tool for collecting ETF data and running optimizations on this data",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=8.0.1,<8.1',
        'scrapy>=2.5.0,<2.6',
        'selenium>=3.141.0,<4',
        'SQLAlchemy>=1.4.23,<1.5',
        'sqlalchemy-utils>=0.37,<0.38',
        'pandas>=1.3.3,<1.4',
        'requests>=2.26,<2.27',
        'dash>=1.21,<2.0',
        'dash-bootstrap-components>=0.12.0,<0.13',
        'PyPortfolioOpt>=1.4.1,<1.5.0',
        'gurobipy>=9.1.0,<9.2.0',
        'scikit-learn>=0.24.0,<0.25.0',
        'numpy>=1.21.2,<1.22',
        'plotly>=5.3.1,<5.4',
        'openpyxl>=3.0.8,<3.1.0',
        'python-dateutil>=2.8.2,<2.9.0',
        'eikon>=1.1.12,<1.2',
        'appdirs>=1.4.4,<1.5',
        'yfinance>=0.1.63,<0.2'
    ],
    entry_points='''
        [console_scripts]
        etfopt=run:etfopt
    ''',
)
