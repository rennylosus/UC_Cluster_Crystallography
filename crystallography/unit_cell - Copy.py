from __future__ import annotations

import math
from typing import Any

from core.models import UnitCell


def calculate_volume(cell: UnitCell) -> float:
    """
    Calculate the unit-cell volume in Å³.
    """

    alpha = math.radians(cell.alpha)
    beta = math.radians(cell.beta)
    gamma = math.radians(cell.gamma)

    factor = (
        1
        - math.cos(alpha) ** 2
        - math.cos(beta) ** 2
        - math.cos(gamma) ** 2
        + 2
        * math.cos(alpha)
        * math.cos(beta)
        * math.cos(gamma)
    )

    if factor <= 0:
        raise ValueError(
            "Invalid unit-cell geometry: "
            "volume factor is not positive."
        )

    return (
        cell.a
        * cell.b
        * cell.c
        * math.sqrt(factor)
    )


def cell_to_tuple(
    cell: UnitCell,
) -> tuple[float, float, float, float, float, float]:
    """Return a UnitCell as (a, b, c, alpha, beta, gamma)."""

    return cell.as_tuple()


def cell_from_tuple(
    values: tuple[float, float, float, float, float, float],
    source: str = "",
) -> UnitCell:
    """
    Create a UnitCell from six parameters.
    """

    if len(values) != 6:
        raise ValueError(
            "A unit cell requires exactly six parameters."
        )

    cell = UnitCell(
        a=float(values[0]),
        b=float(values[1]),
        c=float(values[2]),
        alpha=float(values[3]),
        beta=float(values[4]),
        gamma=float(values[5]),
        source=source,
    )

    if not cell.is_valid():
        raise ValueError(
            "Invalid unit-cell parameters."
        )

    return cell


def volume_difference(
    cell1: UnitCell,
    cell2: UnitCell,
) -> float:
    """Return the absolute volume difference in Å³."""

    return abs(
        calculate_volume(cell1)
        - calculate_volume(cell2)
    )


def volume_difference_percent(
    cell1: UnitCell,
    cell2: UnitCell,
) -> float:
    """
    Return the absolute volume difference as a percentage
    relative to cell1.
    """

    volume1 = calculate_volume(cell1)
    volume2 = calculate_volume(cell2)

    if volume1 == 0:
        raise ZeroDivisionError(
            "Cannot calculate percentage difference "
            "for a zero-volume cell."
        )

    return abs(volume2 - volume1) / volume1 * 100.0


def to_gemmi(
    cell: UnitCell,
) -> Any:
    """
    Convert our UnitCell to a gemmi.UnitCell.

    Gemmi is imported lazily so that the rest of the project
    can operate without Gemmi installed.
    """

    try:
        import gemmi
    except ImportError as exc:
        raise ImportError(
            "Gemmi is required for this operation. "
            "Install it with: pip install gemmi"
        ) from exc

    return gemmi.UnitCell(
        cell.a,
        cell.b,
        cell.c,
        cell.alpha,
        cell.beta,
        cell.gamma,
    )


def from_gemmi(
    gemmi_cell: Any,
    source: str = "GEMMI",
) -> UnitCell:
    """
    Convert a gemmi.UnitCell to our UnitCell representation.
    """

    cell = UnitCell(
        a=float(gemmi_cell.a),
        b=float(gemmi_cell.b),
        c=float(gemmi_cell.c),
        alpha=float(gemmi_cell.alpha),
        beta=float(gemmi_cell.beta),
        gamma=float(gemmi_cell.gamma),
        source=source,
    )

    if not cell.is_valid():
        raise ValueError(
            "Gemmi returned an invalid unit cell."
        )

    return cell


def reduce_cell(
    cell: UnitCell,
    method: str = "niggli",
) -> UnitCell:
    """
    Reduce a unit cell using Gemmi.

    Supported methods:

        niggli
        buerger
    """

    try:
        import gemmi
    except ImportError as exc:
        raise ImportError(
            "Gemmi is required for cell reduction. "
            "Install it with: pip install gemmi"
        ) from exc

    gemmi_cell = to_gemmi(cell)

    method = method.lower().strip()

    # The current project does not yet provide lattice
    # centring or space-group information, so None is used.
    gruber = gemmi.GruberVector(
        gemmi_cell,
        None,
    )

    if method == "niggli":

        gruber.niggli_reduce()

    elif method == "buerger":

        gruber.buerger_reduce()

    else:

        raise ValueError(
            f"Unsupported cell-reduction method: {method}. "
            "Use 'niggli' or 'buerger'."
        )

    reduced = gruber.get_cell()

    return from_gemmi(
        reduced,
        source=f"GEMMI-{method.upper()}",
    )


def cell_is_valid(
    cell: UnitCell,
) -> bool:
    """Return whether the unit cell passes basic validation."""

    return cell.is_valid()