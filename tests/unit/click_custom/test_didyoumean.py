import pytest

from anymotion_cli.click_custom.didyoumean import DYMMixin

CMD_LIST = [
    "analysis",
    "analyze",
    "compare",
    "comparison",
    "configure",
    "download",
    "draw",
    "drawing",
    "extract",
    "image",
    "keypoint",
    "movie",
    "upload",
]


@pytest.mark.parametrize(
    "command, error_msg, expected",
    [
        (
            "images",
            "Error: No such command 'images'.",
            "\n\nDid you mean this?\n\timage",
        ),
        (
            "load",
            "Error: No such command 'load'.",
            "\n\nDid you mean one of these?\n\tupload\n\tdownload",
        ),
    ],
)
def test_create_error_msg(command, error_msg, expected):
    obj = DYMMixin()
    res = obj._create_error_msg(error_msg, command, CMD_LIST)

    assert res == error_msg + expected
