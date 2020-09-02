<div align="center"><a href="https://anymotion.nttpc.co.jp/"><img src="https://user-images.githubusercontent.com/63082802/81498974-edf9a500-9302-11ea-8583-f8d6971a9b25.png"/></a></div>

# AnyMotion CLI

[![PyPi][pypi-version]][pypi] [![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

This package provides a command line interface to [AnyMotion](https://anymotion.nttpc.co.jp/), which is a motion analysis API using pose estimation.
It uses the [AnyMotion Python SDK](https://github.com/nttpc/anymotion-python-sdk).

<div align="center"><img src="https://user-images.githubusercontent.com/63082802/81499044-7a0bcc80-9303-11ea-96b5-a779ae0adcf7.gif"/></div>

It works on Python versions:

- Python 3.6
- Python 3.7
- Python 3.8

## Installation

Install using [pip](https://pip.pypa.io/en/stable/quickstart/):

```sh
$ pip install anymotion-cli
```

Alternatively, you can use [homebrew](https://brew.sh/) to install:

```sh
$ brew install nttpc/tap/anymotion-cli
```

## Getting Started

Before using anymotion-cli, you need to tell it about your credentials which issued by the [AnyMotion Portal](https://portal.anymotion.jp/).
You can do this in several ways:

- CLI command
- Credentials file
- Environment variables

The quickest way to get started is to run the `amcli configure` command:

```sh
$ amcli configure
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

You can use `amcli`.

```text
amcli [OPTIONS] COMMAND [ARGS]...
```

See the table below for more information, or run it with the `--help` option.

### Commands to process something (verb commands)

| command name | description |
| -- | -- |
| upload | Upload the local movie or image file to the cloud storage. |
| download | Download the drawn file. |
| extract | Extract keypoints from uploaded images or movies. |
| analyze | Analyze the extracted keypoint data. |
| compare | Compare the two extracted keypoint data |
| draw | Draw based on the extracted keypoints or comparison results. |

### Commands to show something (noun commands)

| command name | description |
| -- | -- |
| image | Show the information of the uploaded images. |
| movie | Show the information of the uploaded movies. |
| keypoint | Show the extracted keypoints. |
| analysis | Show the analysis results. |
| comparison | Show the comparison results. |
| drawing | Show the information of the drawn images or movies. |

### Other commands

| command name | description |
| -- | -- |
| configure | Configure your AnyMotion Credentials. |

### Examples

#### Draw keypoints in image file

First, upload the image file.

```sh
$ amcli upload image.jpg
Success: Uploaded image.jpg to the cloud storage. (image id: 111)
```

When the upload is complete, you will get an `image id`.
Extract keypoints using this `image id`.

```sh
$ amcli extract --image-id 111
Keypoint extraction started. (keypoint id: 222)
Success: Keypoint extraction is complete.
```

Draw points/lines to image using `keypoint id`.

```sh
$ amcli draw --keypoint-id 222
Drawing is started. (drawing id: 333)
Success: Drawing is complete.
Downloaded the file to image.jpg.
```

When the drawing is complete, the drawing file is downloaded (by default, to the current directory).
To save to a specific file or directory, use the `--out` option.

#### Draw using rules

You can use the rules to draw a variety of things.
In the following example, draw the lines of stick picture in red.

```sh
$ amcli draw --keypoint-id 222 --rule '{"drawingType": "stickPicture", "pattern": "all", "color": "red"}'
```

In the following other example, draw only the skeleton.

```sh
$ amcli draw --keypoint-id 222 --bg-rule '{"skeletonOnly": true}'
```

You can also specify it in the JSON file.

```sh
$ amcli draw --keypoint-id 222 --rule-file rule.json
```

```json
{
  "drawingType": "stickPicture",
  "pattern": "all",
  "color": "red"
}
```

You can also write `rule` and `backgroundRule` at the same time when using `--rule-file`.

```json
{
    "rule": {
        "drawingType": "stickPicture",
        "pattern": "all",
        "color": "red"
    },
    "backgroundRule": {
        "skeletonOnly": true
    }
}
```

For more information on the drawing rules, see the [documentation](https://docs.anymotion.jp/drawing.html).

#### Show extracted keypoints

You can use the `keypoint show` command to display the extracted keypoint data.

```sh
$ amcli keypoint show 1234
{
  "id": 1234,
  "image": null,
  "movie": 123,
  "keypoint": [
    {
      "leftKnee": [
        487,
        730
      ],
      ...
```

The `--only` option allows you to display only the keypoint data.

```sh
$ amcli keypoint show 1234 --only
[
  {
    "leftKnee": [
      487,
      730
    ],
    "rightKnee": [
      1118,
      703
    ]
    ...
```

With [jq](https://stedolan.github.io/jq/), it's also easy to take out only certain parts of the body.

```sh
$ amcli keypoint show 1234 --only | jq '[.[].leftKnee]'
[
  [
    487,
    730
  ],
  null,
  null,
  ...
```

The `--join` option also allows you to display related data.

```sh
$ amcli keypoint show 1234 --join
{
  "id": 1234,
  "image": null,
  "movie": {
    "id": 123,
    "name": "movie",
    "text": "Created by anymotion-cli.",
    ...
  "keypoint": [
    {
      "leftKnee": [
        487,
        730
      ],
      ...
```

## Shell Complete

The anymotion-cli supports Shell completion.

For Bash, add this to `~/.bashrc`:

```sh
eval "$(_AMCLI_COMPLETE=source amcli)"
```

For Zsh, add this to `~/.zshrc`:

```sh
eval "$(_AMCLI_COMPLETE=source_zsh amcli)"
```

For Fish, add this to `~/.config/fish/completions/amcli.fish`:

```sh
eval (env _AMCLI_COMPLETE=source_fish amcli)
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).

## Contributing

- Code must work on Python 3.6 and higher.
- Code should follow [black](https://black.readthedocs.io/en/stable/).
- Docstring should follow [Google Style](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Install all development dependencies using:

  ```sh
  $ poetry install
  ```

- You can install a pre-commit hook to check:

  ```sh
  $ poetry run pre-commit install
  ```

- Before submitting pull requests, run tests with:

  ```sh
  $ poetry run tox
  ```

[pypi]: https://pypi.org/project/anymotion-cli
[pypi-version]: https://img.shields.io/pypi/v/anymotion-cli
[ci]: https://circleci.com/gh/nttpc/anymotion-cli
[ci-status]: https://circleci.com/gh/nttpc/anymotion-cli.svg?style=shield&circle-token=4f7564ae447f53ff1c6d3aadb2303b5d526c6fb8
[codecov]: https://codecov.io/gh/nttpc/anymotion-cli
[codecov-status]: https://codecov.io/gh/nttpc/anymotion-cli/branch/master/graph/badge.svg?token=6S0GIV4ZD9
