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
$ pip install git+ssh://git@bitbucket.org/nttpc-datascience/encore-api-cli.git
```

## Getting Started

Before encore-api-cli, you need to tell it about your AnyMotion credentials.

``` sh
$ encore configure
AnyMotion API URL [https://api.customer.jp/]:
AnyMotion Client ID: your_client_id
AnyMotion Client Secret: your_client_secret
```

and create an INI formatted file.
Then, place it in `~/.anymotion/config`.

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
  analysis   Manege analyses.
  analyze    Analyze keypoints data and get information such as angles.
  configure  Configure your AnyMotion Access Token.
  draw       Draw keypoints on uploaded movie or image.
  image      Manege images.
  keypoint   Extract keypoints and show the list.
  movie      Manege movies.
  upload     Upload a local movie or image to cloud storage.
```

### Examples

#### Draw keypoints in image file

First, upload the image file.

``` sh
$ encore upload image.jpg
Uploaded the image file to cloud storage (image_id: 111)
```

When the upload is complete, you get an `image_id`. Extract keypoints using this `image_id`.

``` sh
$ encore keypoint extract --image_id 111 --with_drawing
Extract keypoint (keypoint_id: 222)
.
Keypoint extraction is complete.
Draw keypoint (drawing_id: 333)
.
Keypoint drawing is complete.
Downloaded the file to image_xxx.jpg.
```

When the drawing is complete, the drawing file is downloaded (by default, to the current directory).

### Tips

You can use [jq](https://stedolan.github.io/jq/) to filter according to conditions.

``` sh
# Get a list of keypoints whose exec_status is SUCCESS
$ encore keypoint list | jq '.[] | select(.exec_status == "SUCCESS"  | {id: .id, image: .image, movie: .movie}'

# Get a list of keypoint_id for only movie
$ encore keypoint list | jq '.[] | select(.movie != null) | .id'
```
