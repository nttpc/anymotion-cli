# AnyMotion CLI

[![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

This package provides a command line interface to [AnyMotion](https://anymotion.nttpc.co.jp/).

It works on Python versions:

- Python 3.6
- Python 3.7
- Python 3.8

## Installation

Install using [pip](https://pip.pypa.io/en/stable/quickstart/):

```sh
$ pip install anymotion-cli
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
AnyMotion API URL [https://api.customer.jp/anymotion/v1/]:
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

More information, see below tables or run with `--help` option.

### Commands to process something (verb commands)

| command name | description |
| -- | -- |
| upload | Upload the local movie or image file to the cloud storage. |
| download | Download the drawn file. |
| extract | Extract keypoints from uploaded images or movies. |
| draw | Draw points and/or lines on uploaded movie or image. |
| analyze | Analyze the extracted keypoint data. |

### Commands to show something (noun commands)

| command name | description |
| -- | -- |
| image | Show the information of the uploaded images. |
| movie | Show the information of the uploaded movies. |
| keypoint | Show the extracted keypoints. |
| drawing | Show the information of the drawn images or movies. |
| analysis | Show the analysis results. |

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

When the upload is complete, you get an `image id`.
Extract keypoints using this `image id`.

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
Downloaded the file to image.jpg.
```

When the drawing is complete, the drawing file is downloaded (by default, to the current directory).
To save to a specific file or directory, use the `--out` option.

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

- Before submitting pull requests, run tests with:

  ```sh
  $ poetry run tox
  ```

[ci]: https://circleci.com/gh/nttpc/anymotion-cli
[ci-status]: https://circleci.com/gh/nttpc/anymotion-cli.svg?style=shield&circle-token=4f7564ae447f53ff1c6d3aadb2303b5d526c6fb8
[codecov]: https://codecov.io/gh/nttpc/anymotion-cli
[codecov-status]: https://codecov.io/gh/nttpc/anymotion-cli/branch/master/graph/badge.svg?token=6S0GIV4ZD9
