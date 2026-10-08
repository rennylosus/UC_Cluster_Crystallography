from datetime import datetime
from pathlib import Path

from config import (
    DEBUG,
    DEBUG_RODHYPIX,
    RODHYPIX_EXTENSION,
    RODHYPIX_FOLDER_NAME,
    RODHYPIX_RECURSIVE,
)


def debug_print(message: str) -> None:
    """Print a debug message when RODHYPIX debugging is enabled."""

    if DEBUG and DEBUG_RODHYPIX:
        print(message)


def find_first_rodhypix(
    dataset_folder: Path,
) -> Path | None:
    """
    Find the first .rodhypix file in the dataset's frames directory.

    By default only the files directly inside:

        dataset/frames/

    are inspected.

    If RODHYPIX_RECURSIVE is True, subdirectories inside frames/
    are also searched.
    """

    frames_dir = (
        dataset_folder / RODHYPIX_FOLDER_NAME
    )

    debug_print(
        f"  Looking for .rodhypix in: {frames_dir}"
    )

    if not frames_dir.is_dir():

        debug_print(
            "    frames directory not found"
        )

        return None

    # --------------------------------------------------------
    # Select search method
    # --------------------------------------------------------

    if RODHYPIX_RECURSIVE:

        iterator = frames_dir.rglob(
            f"*{RODHYPIX_EXTENSION}"
        )

    else:

        iterator = frames_dir.glob(
            f"*{RODHYPIX_EXTENSION}"
        )

    # --------------------------------------------------------
    # Find first file
    # --------------------------------------------------------

    for file in iterator:

        if not file.is_file():
            continue

        debug_print(
            f"    Found .rodhypix: {file}"
        )

        return file

    debug_print(
        "    No .rodhypix found"
    )

    return None


def get_rodhypix_modification_date(
    rodhypix_file: Path | None,
) -> datetime | None:
    """
    Return the filesystem modification date of a .rodhypix file.

    Returns None if the file does not exist or its metadata
    cannot be accessed.
    """

    if rodhypix_file is None:
        return None

    try:

        modification_time = (
            rodhypix_file.stat().st_mtime
        )

        return datetime.fromtimestamp(
            modification_time
        )

    except (OSError, ValueError) as exc:

        print(
            "WARNING: Could not obtain modification "
            f"date for {rodhypix_file}: {exc}"
        )

        return None