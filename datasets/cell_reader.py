from __future__ import annotations

from pathlib import Path

from config import DEBUG, DEBUG_CELL
from core.models import UnitCell


def debug_print(message: str) -> None:
    if DEBUG and DEBUG_CELL:
        print(message)


def read_unit_cell(
    ins_file: Path | str | None,
) -> UnitCell | None:
    """
    Read the first valid SHELX CELL instruction from an INS file.

    Expected format:

        CELL wavelength a b c alpha beta gamma

    The wavelength is ignored.

    Returns:
        UnitCell if a valid CELL instruction is found.
        None otherwise.
    """

    if ins_file is None:
        debug_print(
            "    No .ins file; unit cell unavailable."
        )
        return None

    ins_file = Path(ins_file)

    if not ins_file.is_file():
        debug_print(
            f"    INS file does not exist: {ins_file}"
        )
        return None

    debug_print(
        f"    Reading unit cell from: {ins_file}"
    )

    try:
        with ins_file.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):
                line = line.strip()

                if not line:
                    continue

                if not line.upper().startswith("CELL"):
                    continue

                parts = line.split()

                # CELL wavelength a b c alpha beta gamma
                if len(parts) < 8:
                    debug_print(
                        "    Invalid CELL line at "
                        f"line {line_number}: {line}"
                    )
                    continue

                try:
                    # Wavelength is deliberately ignored.
                    float(parts[1])

                    a = float(parts[2])
                    b = float(parts[3])
                    c = float(parts[4])

                    alpha = float(parts[5])
                    beta = float(parts[6])
                    gamma = float(parts[7])

                except ValueError:
                    debug_print(
                        "    Could not parse CELL line "
                        f"at line {line_number}"
                    )
                    continue

                cell = UnitCell(
                    a=a,
                    b=b,
                    c=c,
                    alpha=alpha,
                    beta=beta,
                    gamma=gamma,
                    source="INS",
                )

                if not cell.is_valid():
                    debug_print(
                        "    Invalid unit-cell parameters "
                        f"at line {line_number}"
                    )
                    continue

                debug_print(
                    "    INS unit cell found: "
                    f"a={a}, "
                    f"b={b}, "
                    f"c={c}, "
                    f"alpha={alpha}, "
                    f"beta={beta}, "
                    f"gamma={gamma}"
                )

                return cell

    except Exception as exc:
        print(
            f"WARNING: Could not read {ins_file}: {exc}"
        )
        return None

    debug_print(
        "    No valid CELL line found."
    )

    return None