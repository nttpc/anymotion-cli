# Encore API CLI

Command Line Interface for AnyMotion API.

## インストール方法

``` sh
pip install git+ssh://git@bitbucket.org/nttpc-datascience/encore-api-cli.git
```

## 使い方

``` sh
encore --help
```

``` text
Usage: encore [OPTIONS] COMMAND [ARGS]...

  Command Line Interface for AnyMotion API.

Options:
  --token TEXT  Access token for authorization.  [required]
  --url TEXT    URL of AnyMotion API.  [default:
                https://dev.api.anymotion.jp/api/v1/]
  --help        Show this message and exit.

Commands:
  analysis  Analyze keypoints data and get information such as angles.
  drawing   Draw keypoints on uploaded movie or image.
  image     Manege images.
  keypoint  Extract keypoints and show the list.
  movie     Manege movies.
  upload    Upload a local movie or image to cloud storage.
```

### 便利な使い方

[jq](https://stedolan.github.io/jq/) と組み合わせることで、条件でフィルタリングや整形をすることができます。

``` sh
# exec_statusがSUCCESSであるkeypoint一覧を取得
encore keypoint list | jq '.data[] | select(.exec_status == "SUCCESS"  | {id: .id, image: .image, movie: .movie}'

# 動画に対するkeypoit_idの一覧を取得
encore keypoint list | jq '.data[] | select(.movie != null) | .id'
```
