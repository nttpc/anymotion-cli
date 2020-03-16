import os
from pathlib import Path


def get_app_dir() -> Path:
    """Get application root directory."""
    app_dir = Path(os.getenv("ANYMOTION_ROOT", Path.home())) / ".anymotion"
    app_dir.mkdir(exist_ok=True)
    return app_dir


# default values
API_URL = "https://api.customer.jp/anymotion/v1/"
POLLING_INTERVAL = 5
TIMEOUT = 600
IS_DOWNLOAD = True
IS_OPEN = False
