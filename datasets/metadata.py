from pathlib import Path

from config import (
    DEBUG,
    DEBUG_SIZE,
    SIZE_UNIT,
)


def debug_print(message: str) -> None:
    """Print a debug message when size debugging is enabled."""

    if DEBUG and DEBUG_SIZE:
        print(message)


def get_folder_size(
    folder: Path,
) -> float:
    """
    Calculate the total size of all files inside a folder.

    The calculation is recursive because the requested value
    represents the total size of the complete dataset folder.

    SIZE_UNIT is configured in config.py and can be:

        B
        KB
        MB
        GB
    """

    total_bytes = 0

    debug_print(
        f"  Calculating folder size: {folder}"
    )

    try:

        for path in folder.rglob("*"):

            if not path.is_file():
                continue

            try:

                total_bytes += path.stat().st_size

            except (OSError, PermissionError) as exc:

                print(
                    f"WARNING: Could not read size of "
                    f"{path}: {exc}"
                )

    except (OSError, PermissionError) as exc:

        print(
            f"WARNING: Could not calculate size of "
            f"{folder}: {exc}"
        )

    # --------------------------------------------------------
    # Convert bytes
    # --------------------------------------------------------

    unit = SIZE_UNIT.upper()

    if unit == "B":

        size = float(total_bytes)

    elif unit == "KB":

        size = total_bytes / 1024

    elif unit == "MB":

        size = total_bytes / (1024 ** 2)

    elif unit == "GB":

        size = total_bytes / (1024 ** 3)

    else:

        print(
            f"WARNING: Unknown SIZE_UNIT '{SIZE_UNIT}'. "
            "Using MB."
        )

        size = total_bytes / (1024 ** 2)

    debug_print(
        f"    Size = {size:.2f} {SIZE_UNIT}"
    )

    return size