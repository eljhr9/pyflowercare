import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO", format_string: Optional[str] = None, include_timestamp: bool = True
) -> None:
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()), format=format_string, stream=sys.stdout
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"flowercare.{name}")


def disable_bleak_logs() -> None:
    logging.getLogger("bleak").setLevel(logging.WARNING)
    logging.getLogger("bleak.backends").setLevel(logging.WARNING)
