"""Configuration file for unesco_reader"""

from pathlib import Path


class PATHS:
    """Paths"""

    package = Path(__file__).resolve().parent.parent

    BASE_URL = "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/"

    DATASETS = package / 'unesco_reader' / 'glossaries'

