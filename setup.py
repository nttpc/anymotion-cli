import codecs
import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


setup(name='encore-api-cli',
      version=find_version('encore_api_cli', '__init__.py'),
      description='Command Line Interface for AnyMotion API.',
      author='Yusuke Kumihashi',
      author_email='y_kumiha@nttpc.co.jp',
      url='https://bitbucket.org/nttpc-datascience/encore-api-cli',
      entry_points={'console_scripts': ['encore = encore_api_cli.cli:main']},
      packages=find_packages(exclude=('tests', 'docs')),
      install_requires=['click', 'requests'])
