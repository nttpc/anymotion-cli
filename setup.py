from setuptools import find_packages, setup

import encore_api_cli

setup(
    name="encore-api-cli",
    version=encore_api_cli.__version__,
    description=encore_api_cli.__doc__.strip(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yusuke Kumihashi",
    author_email="y_kumiha@nttpc.co.jp",
    url="https://bitbucket.org/nttpc-datascience/encore-api-cli",
    entry_points={
        "console_scripts": [
            "encore = encore_api_cli.cli:cli",
            "amcli = encore_api_cli.cli:cli",
        ]
    },
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.6",
    install_requires=["click", "pygments", "requests", "tabulate", "yaspin"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
