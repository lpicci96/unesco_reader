"""Configuration file for unesco_reader"""

from pathlib import Path
import logging


class PATHS:
    """Paths"""

    package = Path(__file__).resolve().parent.parent

    DATASETS = package / "src" / "unesco_reader" / "glossaries"

    TEST_FILES = package / "tests" / "test_files"


# =========================================
# Configure Logging
# =========================================

logger = logging.getLogger(__name__)
# Create terminal handler
shell_handler = logging.StreamHandler()
# Set levels for the logger, shell and file
logger.setLevel(logging.DEBUG)
shell_handler.setLevel(logging.DEBUG)
# Format the outputs
fmt_file = "%(levelname)s (%(asctime)s): %(message)s"
fmt_shell = (
    "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
)
# Create formatters
shell_formatter = logging.Formatter(fmt_shell)
# Add formatters to handlers
shell_handler.setFormatter(shell_formatter)
# Add handlers to the logger
logger.addHandler(shell_handler)
