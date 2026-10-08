from __future__ import annotations

import logging

from config import DEBUG


def setup_logging(
    level: int | None = None,
) -> logging.Logger:
    """
    Configure and return the main project logger.

    Parameters
    ----------
    level
        Optional logging level. If omitted, DEBUG is used when
        DEBUG=True and INFO otherwise.
    """

    if level is None:

        level = (
            logging.DEBUG
            if DEBUG
            else logging.INFO
        )

    logger = logging.getLogger(
        "RA3_Crystallography"
    )

    logger.setLevel(level)

    # Avoid adding multiple handlers if setup_logging()
    # is called more than once.
    if not logger.handlers:

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s",
            datefmt="%H:%M:%S",
        )

        handler.setFormatter(
            formatter
        )

        logger.addHandler(
            handler
        )

    return logger


def get_logger(
    name: str | None = None,
) -> logging.Logger:
    """
    Return a project logger.

    Examples
    --------
    get_logger()
    get_logger("datasets")
    get_logger("cap")
    """

    logger_name = (
        "RA3_Crystallography"
        if not name
        else f"RA3_Crystallography.{name}"
    )

    return logging.getLogger(
        logger_name
    )