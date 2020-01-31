# Encore API CLI

[![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

This package provides a command line interface to AnyMotion.

The encore-api-cli package works on Python versions:

- Python 3.6
- Python 3.7
- Python 3.8

## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/).

### Latest version

**NOTICE**: You need an SSH key to install.

```sh
$ pip install -U git+ssh://git@bitbucket.org/nttpc-datascience/encore-api-cli.git
```

### Specific version

**NOTICE**: You can only install from the internal network.

```sh
$ pip install -U https://encore-api-cli.s3-ap-northeast-1.amazonaws.com/encore_api_cli-<version>-py3-none-any.whl
```

To install version 1.0.0:

```sh
$ pip install -U https://encore-api-cli.s3-ap-northeast-1.amazonaws.com/encore_api_cli-1.0.0-py3-none-any.whl
```

## Getting Started

Before using encore-api-cli, you need to tell it about your AnyMotion credentials.
You can do this in several ways:

- CLI command
- Credentials file
- Environment variables

The quickest way to get started is to run the `amcli configure` command:

```sh
$ amcli configure
AnyMotion API URL [https://api.customer.jp/]:
AnyMotion Client ID: your_client_id
AnyMotion Client Secret: your_client_secret
```

To use environment variables, do the following:

```sh
export ANYMOTION_CLIENT_ID=<your_client_id>
export ANYMOTION_CLIENT_SECRET=<your_client_secret>
```

To use the credentials file, create an INI formatted file like this:

```text
[default]
anymotion_client_id=<your_client_id>
anymotion_client_secret=<your_client_secret>
```

and place it in `~/.anymotion/credentials`.

**Note**: If set in both the credentials file and environment variables, the environment variables takes precedence.

## Usage

```sh
$ amcli --help
```

```text
Usage: amcli [OPTIONS] COMMAND [ARGS]...

  Command Line Interface for AnyMotion API.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analysis   Show analysis results.
  analyze    Analyze the extracted keypoint data.
  configure  Configure your AnyMotion Credentials.
  download   Download the drawn file.
  draw       Draw points and/or lines on uploaded movie or image.
  drawing    Show the information of the drawn images or movies.
  extract    Extract keypoints from uploaded images or movies.
  image      Show the information of the uploaded images.
  keypoint   Show the extracted keypoints.
  movie      Show the information of the uploaded movies.
  upload     Upload the local movie or image file to the cloud storage.
```

- Commands to process something (verb commands)
  - upload
  - download
  - extract
  - draw
  - analyze

- Commands to show something (noun commands)
  - image
  - movie
  - keypoint
  - drawing
  - analysis

### Examples

#### Draw keypoints in image file

First, upload the image file.

```sh
$ amcli upload image.jpg
Success: Uploaded image.jpg to the cloud storage. (image id: 111)
```

When the upload is complete, you get an `image id`. Extract keypoints using this `image id`.

```sh
$ amcli extract --image-id 111
Keypoint extraction started. (keypoint id: 222)
Success: Keypoint extraction is complete.
```

Draw points/lines to image using `keypoint id`.

```sh
$ amcli draw 222
Drawing is started. (drawing id: 333)
Success: Drawing is complete.
Downloaded the file to image_xxx.jpg.
```

When the drawing is complete, the drawing file is downloaded (by default, to the current directory).
To save to a specific directory, use the `--out-dir` option.

### Tips

You can use [jq](https://stedolan.github.io/jq/) to filter according to conditions.

Get a list of keypoints whose execStatus is SUCCESS:

```sh
$ amcli keypoint list | jq '.[] | select(.execStatus == "SUCCESS"  | {id: .id, image: .image, movie: .movie}'
```

Get a list of keypoint_id for only movie:

```sh
$ amcli keypoint list | jq '.[] | select(.movie != null) | .id'
```

## Bash Complete

The encore-api-cli supports Bash completion.
To enable Bash completion, you would need to put into your `.bashrc`:

```sh
$ eval "$(_AMCLI_COMPLETE=source amcli)"
```

For zsh users add this to your `.zshrc`:

```sh
$ eval "$(_AMCLI_COMPLETE=source_zsh amcli)"
```

## Contributing

- Code must work on Python 3.6 and higher.
- Code should follow [black](https://black.readthedocs.io/en/stable/).
- Docstring should follow [Google Style](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Install all development dependencies using:

```sh
$ poetry install
```

- Before submitting pull requests, run tests with:

```sh
$ poetry run tox
```

[ci]: https://circleci.com/bb/nttpc-datascience/encore-api-cli/tree/master
[ci-status]: https://circleci.com/bb/nttpc-datascience/encore-api-cli/tree/master.svg?style=shield&circle-token=8efda4c7b7ec1fe9abff9fac5412bd9a59604c84
[codecov]: https://codecov.io/bb/nttpc-datascience/encore-api-cli
[codecov-status]: https://codecov.io/bb/nttpc-datascience/encore-api-cli/branch/master/graph/badge.svg?token=s4c1X9EhAN
