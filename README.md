# Encore API CLI

[![CircleCI](https://circleci.com/bb/nttpc-datascience/encore-api-cli/tree/master.svg?style=shield&circle-token=8efda4c7b7ec1fe9abff9fac5412bd9a59604c84)](https://circleci.com/bb/nttpc-datascience/encore-api-cli/tree/master) [![codecov](https://codecov.io/bb/nttpc-datascience/encore-api-cli/branch/master/graph/badge.svg?token=s4c1X9EhAN)](https://codecov.io/bb/nttpc-datascience/encore-api-cli)

This package provides a command line interface to AnyMotion.

The encore-api-cli package works on Python versions:

- Python 3.6
- Python 3.7
- Python 3.8

## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

``` sh
$ pip install -U git+ssh://git@bitbucket.org/nttpc-datascience/encore-api-cli.git
```

## Getting Started

Before using encore-api-cli, you need to tell it about your AnyMotion credentials.
You can do this in several ways:

- Credentials file
- Environment variables

The quickest way to get started is to run the `encore configure` command:

``` sh
$ encore configure
AnyMotion API URL [https://api.customer.jp/]:
AnyMotion Client ID: your_client_id
AnyMotion Client Secret: your_client_secret
```

To use environment variables, do the following:

``` sh
export ANYMOTION_CLIENT_ID=<your_client_id>
export ANYMOTION_CLIENT_SECRET=<your_client_secret>
```

To use the credentials file, create an INI formatted file like this:

``` text
[default]
anymotion_client_id=<your_client_id>
anymotion_client_secret=<your_client_secret>
```

and place it in `~/.anymotion/credentials`.

**Note**: If set in both the credentials file and environment variables, the environment variables takes precedence.

## Usage

``` sh
$ encore --help
```

``` text
Usage: encore [OPTIONS] COMMAND [ARGS]...

  Command Line Interface for AnyMotion API.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analysis   Show analysis results.
  analyze    Analyze the extracted keypoint data.
  configure  Configure your AnyMotion Credentials.
  draw       Draw keypoints on uploaded movie or image.
  image      Show the information of the uploaded images.
  keypoint   Extract keypoints and show the list.
  movie      Show the information of the uploaded movies.
  upload     Upload the local movie or image file to the cloud storage.
```

### Examples

#### Draw keypoints in image file

First, upload the image file.

``` sh
$ encore upload image.jpg
Success: Uploaded image.jpg to the cloud storage. (image_id: 111)
```

When the upload is complete, you get an `image_id`. Extract keypoints using this `image_id`.

``` sh
$ encore keypoint extract --image_id 111
Keypoint extraction started. (keypoint_id: 222)
Success: Keypoint extraction is complete.
```

``` sh
$ encore draw --keypoint_id 222
Drawing is started. (drawing_id: 333)
Success: Drawing is complete.
Downloaded the file to image_xxx.jpg.
```

When the drawing is complete, the drawing file is downloaded (by default, to the current directory).
To save to a specific directory, use the ``--out_dir`` option.

### Tips

You can use [jq](https://stedolan.github.io/jq/) to filter according to conditions.

Get a list of keypoints whose exec_status is SUCCESS:

``` sh
$ encore keypoint list | jq '.[] | select(.exec_status == "SUCCESS"  | {id: .id, image: .image, movie: .movie}'
```

Get a list of keypoint_id for only movie:

``` sh
$ encore keypoint list | jq '.[] | select(.movie != null) | .id'
```

## Bash Complete

The encore-api-cli supports Bash completion.
To enable Bash completion, you would need to put into your `.bashrc`:

``` sh
$ eval "$(_ENCORE_COMPLETE=source encore)"
```

For zsh users add this to your `.zshrc`:

``` sh
$ eval "$(_ENCORE_COMPLETE=source_zsh encore)"
```

## Contributing

- Code must work on Python 3.6 and higher.
- Code should follow [black](https://black.readthedocs.io/en/stable/).
- Docstring should follow [Google Style](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Install all development dependencies using:

``` sh
$ pipenv install --dev
```

- Before submitting pull requests, run tests with:

``` sh
$ pipenv run tox
```
