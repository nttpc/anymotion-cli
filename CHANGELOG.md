# Change Log

## 0.6.4

Unreleased

- Made it possible to use uppercase extensions.

## 0.6.3

Released 2020-01-20

- Fixed draw bug without rule option.

## 0.6.2

Released 2020-01-20

- Added alias command `amcli`.
- Added rule option in `analyze` and `draw` command.

## 0.6.1

Released 2020-01-09

- Added support for AnyMotion API whose response is camel case.

## 0.6.0

Released 2020-01-07

- Added new `download` command to download the drawn file.
- Added environment variables to the way to tell about credentials.
- Added assertions for some commands and config values.
- Improved display by adding a spinner and adding color.
- Changed to output stdout for each command instead of `Client` class.
- Split the credentials file from the config file.

## 0.5.3

Released 2019-12-26

- Added `--with_drawing` option to keypoint extract command.
- Dropped support for Python 3.5.

## 0.5.2

Released 2019-12-23

- Removed `--rule_id` option.

## 0.5.1

Released 2019-12-23

- Fixed import bug.

## 0.5.0

Released 2019-12-23

- Changed to an authentication format that uses a client id and secret.

## 0.1.0

Released 2019-07-18

- Initial release.
