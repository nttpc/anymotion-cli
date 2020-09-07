# Change Log

- Added "Did you mean ...?" suggestions for missing commands error.
- Added `-h` option as an alias to `--help`.

## 1.1.0

Released 2020-09-02

- Added `compare` and `comparison` commands to be able to use AnyMotion's new feature, comparison.
- Added `--comparison-id` option to `draw` command.
- Added the `--join` option to display the data related to `keypoint show`, `analysis show` and `drawing show` commands at the same time.
- Added `--bg-rule` option in `draw` command.
- Changed from `KEYPOINT_ID` argument to `--keypoint-id` option in `draw` command (**DISRUPTIVE CHANGE**).
- Changed to use [anymotion-sdk](https://github.com/nttpc/anymotion-python-sdk) 1.2.
- Made it possible to draw background using `--rule-file` in `draw` command.
- Improved the display of JSON data response and fixed to not display binary data response when using `-v` option.
- Removed setting API URL in `configure` command.
- Fixed a bug that prevented download without keypoint id.

## 1.0.1

Released 2020-05-11

- Changed the display of non-ASCII characters without escaping.
- Fixed a bug in which the query parameters of some request URLs were not displayed.

## 1.0.0

Released 2020-04-28

- Public release.

## 0.9.1

Released 2020-03-24

- Fixed bug that caused an error with `-v` option when Content-Type header of response is not json.

## 0.9.0

Released 2020-03-17

- Added `--only` option to `keypoint show` and `analysis show` commands.
- Added `--download / --no-download` option to `draw` command.
- Added `--open / --no-open` option to `download` command.
- Moved sdk to another package ~~encore_sdk~~ [anymotion_sdk](https://github.com/nttpc/anymotion-python-sdk).
- Made it possible to handle for changing analysis result response.
- Allowed files with `--out` option.
- Fixed bug when response.reason is None at output.py.

## 0.8.0

Released 2020-02-17

- Added `--interactive` option (You can use interactive mode).
- Added pager (if the text to display is long, you can scroll).
- Added `configure get`, `configure set`, and `configure clear` commands.
- Added color to help display.
- Made hidden the credentials value at `configure` command.
- Moved request method on `encore_api_cli.sdk.client` to `encore_api_cli.sdk.session`.
- Used [s3pypi](https://github.com/novemberfiveco/s3pypi) for release.
- Improved the name of the file to be downloaded.
- Improved error message by catching exceptions.

## 0.7.1

Released 2020-02-06

- Changed API URL format in settings.

## 0.7.0

Released 2020-02-06

- Added `drawing` command.
- Added alias command `enimo`.
- Added the display of failure details when processing fails.
- Added `--status` option to `analysis`, `drawing`, and `keypoint` commands.
- Moved `keypoint extract` subcommand to `extract` command.
- Moved `encore_api_cli.client` to `encore_api_cli.sdk.client`.
- Changed all option names to kebab cases.
- Changed package management from pipenv to poetry.

## 0.6.7

Released 2020-01-29

- Added support for AnyMotion API whose keypoint and result response changed from string to json.

## 0.6.6

Released 2020-01-29

- Allowed object types in rule format.
- Added a restriction that either `--rule` or `--rule-file` option is required in `analyze` command.
- Fixed a bug when interval is less than 1.

## 0.6.5

Released 2020-01-22

- Improved output with `--verbose` option.
- Avoided unnecessary requests to get access token.

## 0.6.4

Released 2020-01-21

- Made it possible to use uppercase extensions.
- Added `--rule-file` option to `analyze` and `draw` commands.
- Fixed a bug without `--rule` option in `analyze` command.

## 0.6.3

Released 2020-01-20

- Fixed a bug without `--rule` option in `draw` command.

## 0.6.2

Released 2020-01-20

- Added alias command `amcli`.
- Added `--rule` option to `analyze` and `draw` commands.

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

- Added `--with_drawing` option to `keypoint extract` command.
- Dropped support for Python 3.5.

## 0.5.2

Released 2019-12-23

- Removed `--rule_id` option.

## 0.5.1

Released 2019-12-23

- Fixed import bug.

## 0.5.0

Released 2019-12-23

- Used client id and secret instead of token for authentication.

## 0.4.0

Released 2019-07-19

- Added `analyze` and `draw` commands.

## 0.3.0

Released 2019-07-19

- Added `configure` command.

## 0.2.0

Released 2019-07-18

- Added `analysis` command.
- Added `list` subcommand.

## 0.1.0

Released 2019-07-18

- Initial release.
