from setuptools import find_packages
from setuptools import setup

import encore_api_cli

setup(name='encore-api-cli',
      version=encore_api_cli.__version__,
      description=encore_api_cli.__doc__,
      author='Yusuke Kumihashi',
      author_email='y_kumiha@nttpc.co.jp',
      url='https://bitbucket.org/nttpc-datascience/encore-api-cli',
      entry_points={'console_scripts': ['encore = encore_api_cli.cli:cli']},
      packages=find_packages(exclude=('tests', 'docs')),
      install_requires=['click', 'requests'])
