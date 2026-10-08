from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from config import (
    ANGLE_TOLERANCE,
    DEBUG,
    DEBUG_PHASE,
    LENGTH_TOLERANCE,
)
from core.models import Dataset, UnitCell


@dataclass
class CellCluster:
    """
    A cluster of Gemmi-reduced unit cells.

    Clustering is performed only on reduced unit cells.
    """
    name: str
    cells: list[UnitCell] = field(default_factory=list)

    @property
    def representative(self) -> UnitCell | None:
        """Return the first reduced cell assigned to the cluster."""
        if not self.cells:
            return None
        return self.cells[0]


class ClusterManager:
    """
    Maintain one global set of clusters during dataset processing.

    Each reduced unit cell is assigned immediately when it becomes
    available. Cluster numbering therefore remains global across
    all datasets while avoiding a separate clustering pass.
    """

    def __init__(
        self,
        length_tolerance: float = LENGTH_TOLERANCE,
        angle_tolerance: float = ANGLE_TOLERANCE,
        phase_prefix: str = "RA3",
    ) -> None:
        self.length_tolerance = length_tolerance
        self.angle_tolerance = angle_tolerance
        self.phase_prefix = phase_prefix
        self.clusters: list[CellCluster] = []

    def assign(self, cell: UnitCell) -> str | None:
        """
        Assign one already-reduced unit cell to a global cluster.

        Returns the cluster name, or None for an invalid cell.
        """
        if not cell.is_valid():
            return None

        for cluster in self.clusters:
            representative = cluster.representative

            if representative is None:
                continue

            if cells_match(
                cell,
                representative,
                length_tolerance=self.length_tolerance,
                angle_tolerance=self.angle_tolerance,
            ):
                cluster.cells.append(cell)

                debug_print(
                    f"    Matched existing cluster: "
                    f"{cluster.name}"
                )

                return cluster.name

        cluster_number = len(self.clusters) + 1
        cluster = CellCluster(
            name=f"{self.phase_prefix}-{cluster_number}",
            cells=[cell],
        )
        self.clusters.append(cluster)

        debug_print(
            f"    New cluster: {cluster.name}"
        )

        return cluster.name

    @property
    def count(self) -> int:
        """Return the number of clusters currently known."""
        return len(self.clusters)


def debug_print(message: str) -> None:
    if DEBUG and DEBUG_PHASE:
        print(message)


def cells_match(
    cell1: UnitCell | None,
    cell2: UnitCell | None,
    length_tolerance: float = LENGTH_TOLERANCE,
    angle_tolerance: float = ANGLE_TOLERANCE,
) -> bool:
    """
    Compare two already-reduced unit cells using absolute tolerances.

    Lengths:
        |a1-a2| <= length_tolerance
        |b1-b2| <= length_tolerance
        |c1-c2| <= length_tolerance

    Angles:
        |alpha1-alpha2| <= angle_tolerance
        |beta1-beta2| <= angle_tolerance
        |gamma1-gamma2| <= angle_tolerance
    """
    if cell1 is None or cell2 is None:
        return False

    if not cell1.is_valid() or not cell2.is_valid():
        return False

    for value1, value2 in zip(
        cell1.as_tuple()[:3],
        cell2.as_tuple()[:3],
    ):
        if abs(value1 - value2) > length_tolerance:
            return False

    for value1, value2 in zip(
        cell1.as_tuple()[3:],
        cell2.as_tuple()[3:],
    ):
        if abs(value1 - value2) > angle_tolerance:
            return False

    return True


def cluster_reduced_cells(
    cells: Iterable[UnitCell],
    length_tolerance: float = LENGTH_TOLERANCE,
    angle_tolerance: float = ANGLE_TOLERANCE,
    phase_prefix: str = "RA3",
) -> list[str]:
    """
    Cluster a collection of already-reduced unit cells.

    This remains available as a convenience function. For the main
    processing pipeline, ClusterManager should be used so that cells
    can be assigned incrementally as they are processed.
    """
    manager = ClusterManager(
        length_tolerance=length_tolerance,
        angle_tolerance=angle_tolerance,
        phase_prefix=phase_prefix,
    )

    assignments: list[str] = []

    for cell in cells:
        cluster_name = manager.assign(cell)
        if cluster_name is not None:
            assignments.append(cluster_name)

    return assignments


def cluster_cap_domains(
    datasets: Iterable[Dataset],
    length_tolerance: float = LENGTH_TOLERANCE,
    angle_tolerance: float = ANGLE_TOLERANCE,
    phase_prefix: str = "RA3",
) -> list[CellCluster]:
    """
    Globally cluster all CAP domains from all datasets.

    Only domain.reduced_unit_cell is used.

    This is retained for compatibility and for batch processing.
    The preferred pipeline implementation is ClusterManager.
    """
    manager = ClusterManager(
        length_tolerance=length_tolerance,
        angle_tolerance=angle_tolerance,
        phase_prefix=phase_prefix,
    )

    for dataset in datasets:
        if dataset.cap_result is None:
            continue

        for domain in dataset.cap_result.domains:
            reduced_cell = domain.reduced_unit_cell

            if reduced_cell is None:
                continue

            domain.cluster = manager.assign(reduced_cell)

    return manager.clusters


def assign_clusters_to_datasets(
    datasets: Iterable[Dataset],
    length_tolerance: float = LENGTH_TOLERANCE,
    angle_tolerance: float = ANGLE_TOLERANCE,
    phase_prefix: str = "RA3",
) -> list[CellCluster]:
    """
    Backward-compatible public name for global CAP-domain clustering.
    """
    return cluster_cap_domains(
        datasets=datasets,
        length_tolerance=length_tolerance,
        angle_tolerance=angle_tolerance,
        phase_prefix=phase_prefix,
    )
