# Encore API CLI

Command Line Interface for AnyMotion API.

## How to install

``` sh
pip install git+ssh://git@bitbucket.org/nttpc-datascience/encore-api-cli.git
```

## Usage

``` sh
encore --help
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

### Tips

You can use [jq](https://stedolan.github.io/jq/) to filter according to conditions.

``` sh
# Get a list of keypoints whose exec_status is SUCCESS
encore keypoint list | jq '.[] | select(.exec_status == "SUCCESS"  | {id: .id, image: .image, movie: .movie}'

# Get a list of keypoit_id for only movie
encore keypoint list | jq '.[] | select(.movie != null) | .id'
```
