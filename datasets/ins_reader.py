from pathlib import Path

from config import (
    DEBUG,
    DEBUG_CELL,
    DEBUG_INS,
    INS_AUTO_SUFFIX,
    INS_EXTENSION,
    INS_OLEX_PREFIX,
    INS_RECURSIVE,
    INS_STRUCT_FOLDER,
)
from core.models import UnitCell


def debug_print(message: str) -> None:
    """Print a debug message when INS debugging is enabled."""

    if DEBUG and DEBUG_INS:
        print(message)


def cell_debug_print(message: str) -> None:
    """Print a debug message when CELL debugging is enabled."""

    if DEBUG and DEBUG_CELL:
        print(message)


def find_ins_file(
    dataset_folder: Path,
) -> Path | None:
    """
    Find the first SHELX .ins file in the expected Olex2
    automatic structure directory.

    Expected structure:

        dataset/
            struct/
                olex2_*_auto/
                    *.ins

    By default, only the direct contents of the
    olex2_*_auto directory are searched.

    If INS_RECURSIVE is enabled, subdirectories are searched too.
    """

    struct_dir = (
        dataset_folder / INS_STRUCT_FOLDER
    )

    debug_print(
        f"  Looking for .ins in: {struct_dir}"
    )

    if not struct_dir.is_dir():
        debug_print(
            "    struct directory not found"
        )
        return None

    try:
        candidates = list(struct_dir.iterdir())

    except (PermissionError, OSError) as exc:
        print(
            f"WARNING: Cannot access {struct_dir}: {exc}"
        )
        return None

    for directory in candidates:

        if not directory.is_dir():
            continue

        name = directory.name

        if not name.startswith(INS_OLEX_PREFIX):
            continue

        if not name.endswith(INS_AUTO_SUFFIX):
            continue

        debug_print(
            f"    Found Olex2 auto directory: "
            f"{directory}"
        )

        if INS_RECURSIVE:
            iterator = directory.rglob(
                f"*{INS_EXTENSION}"
            )
        else:
            iterator = directory.glob(
                f"*{INS_EXTENSION}"
            )

        for file in iterator:

            if not file.is_file():
                continue

            debug_print(
                f"    Found .ins file: {file}"
            )

            return file

    debug_print(
        "    No .ins file found"
    )

    return None


def parse_cell_line(
    line: str,
) -> UnitCell | None:
    """
    Parse a SHELX CELL instruction.

    Expected format:

        CELL wavelength a b c alpha beta gamma

    Example:

        CELL 1.54184 20.839999 20.839999 14.391 90 90 90

    The wavelength is intentionally ignored.
    """

    tokens = line.split()

    if len(tokens) < 8:
        cell_debug_print(
            "    Invalid CELL line: "
            "fewer than 8 values"
        )
        return None

    if tokens[0].upper() != "CELL":
        return None

    try:
        # tokens[1] = wavelength
        a = float(tokens[2])
        b = float(tokens[3])
        c = float(tokens[4])

        alpha = float(tokens[5])
        beta = float(tokens[6])
        gamma = float(tokens[7])

    except ValueError as exc:
        cell_debug_print(
            f"    Could not parse CELL values: {exc}"
        )
        return None

    unit_cell = UnitCell(
        a=a,
        b=b,
        c=c,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        source="INS",
    )

    if not unit_cell.is_valid():
        cell_debug_print(
            "    CELL values failed validation"
        )
        return None

    cell_debug_print(
        "    Parsed unit cell: "
        f"a={a:.6f}, "
        f"b={b:.6f}, "
        f"c={c:.6f}, "
        f"alpha={alpha:.3f}, "
        f"beta={beta:.3f}, "
        f"gamma={gamma:.3f}"
    )

    return unit_cell


def extract_unit_cell(
    ins_file: Path | None,
) -> UnitCell | None:
    """
    Extract the first valid CELL instruction from a SHELX .ins file.
    """

    if ins_file is None:
        cell_debug_print(
            "  No .ins file available; "
            "cannot extract unit cell"
        )
        return None

    debug_print(
        f"  Reading CELL from: {ins_file}"
    )

    try:
        text = ins_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except (OSError, UnicodeError) as exc:
        print(
            f"WARNING: Could not read {ins_file}: {exc}"
        )
        return None

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if not stripped.upper().startswith("CELL"):
            continue

        unit_cell = parse_cell_line(stripped)

        if unit_cell is not None:
            return unit_cell

    cell_debug_print(
        "    No valid CELL instruction found"
    )

    return None