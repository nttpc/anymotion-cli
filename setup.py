from setuptools import setup, find_packages

setup(name='encore-api-cli',
      version='0.1',
      description='Command Line Interface for AnyMotion API.',
      author='Yusuke Kumihashi',
      author_email='y_kumiha@nttcp.co.jp',
      url='https://bitbucket.org/nttpc-datascience/encore-api-cli',
      entry_points={"console_scripts": ["encore = encore_api_cli.cli:main"]},
      packages=find_packages(exclude=('tests', 'docs')),
      install_requires=['click', 'requests'])
