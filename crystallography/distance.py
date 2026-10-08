from __future__ import annotations

import math
from dataclasses import dataclass

from core.models import UnitCell
from crystallography.unit_cell import calculate_volume


@dataclass
class CellDifference:
    """
    Differences between two unit cells.
    """

    da: float
    db: float
    dc: float

    dalpha: float
    dbeta: float
    dgamma: float

    dvolume: float
    dvolume_percent: float

    @property
    def max_length_difference(self) -> float:
        return max(
            abs(self.da),
            abs(self.db),
            abs(self.dc),
        )

    @property
    def max_angle_difference(self) -> float:
        return max(
            abs(self.dalpha),
            abs(self.dbeta),
            abs(self.dgamma),
        )


def compare_cells(
    cell1: UnitCell,
    cell2: UnitCell,
) -> CellDifference:
    """
    Calculate parameter-by-parameter differences between
    two unit cells.
    """

    volume1 = calculate_volume(cell1)
    volume2 = calculate_volume(cell2)

    if volume1 == 0:
        volume_percent = float("inf")
    else:
        volume_percent = (
            abs(volume2 - volume1)
            / volume1
            * 100.0
        )

    return CellDifference(
        da=cell2.a - cell1.a,
        db=cell2.b - cell1.b,
        dc=cell2.c - cell1.c,
        dalpha=cell2.alpha - cell1.alpha,
        dbeta=cell2.beta - cell1.beta,
        dgamma=cell2.gamma - cell1.gamma,
        dvolume=volume2 - volume1,
        dvolume_percent=volume_percent,
    )


def simple_cell_distance(
    cell1: UnitCell,
    cell2: UnitCell,
    length_scale: float = 1.0,
    angle_scale: float = 1.0,
) -> float:
    """
    Calculate a simple Euclidean distance in six-dimensional
    unit-cell parameter space.

    This is useful for exploratory clustering but should not
    be confused with crystallographic reduced-cell matching.
    """

    differences = compare_cells(
        cell1,
        cell2,
    )

    length_terms = (
        differences.da,
        differences.db,
        differences.dc,
    )

    angle_terms = (
        differences.dalpha,
        differences.dbeta,
        differences.dgamma,
    )

    squared_length = sum(
        (value / length_scale) ** 2
        for value in length_terms
    )

    squared_angle = sum(
        (value / angle_scale) ** 2
        for value in angle_terms
    )

    return math.sqrt(
        squared_length
        + squared_angle
    )


def cells_match(
    cell1: UnitCell,
    cell2: UnitCell,
    length_tolerance: float,
    angle_tolerance: float,
) -> bool:
    """
    Determine whether two cells match using the current
    simple parameter-wise tolerance approach.

    This is the legacy/provisional clustering criterion.
    """

    differences = compare_cells(
        cell1,
        cell2,
    )

    return (
        differences.max_length_difference
        <= length_tolerance
        and
        differences.max_angle_difference
        <= angle_tolerance
    )