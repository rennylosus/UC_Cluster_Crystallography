from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

@dataclass
class UnitCell:
    """
    Crystallographic unit-cell parameters.

    All lengths are in Angstrom (Å).
    All angles are in degrees.
    """

    a: float
    b: float
    c: float

    alpha: float
    beta: float
    gamma: float

    # Optional crystallographic information
    lattice_centring: str | None = None
    space_group: str | None = None

    # Where the unit cell came from, e.g.
    # "INS", "CAP", "CCDC"
    source: str = ""

    @property
    def volume(self) -> float:
        """Return unit-cell volume in Å³."""

        import math

        alpha_rad = math.radians(self.alpha)
        beta_rad = math.radians(self.beta)
        gamma_rad = math.radians(self.gamma)

        volume_factor = (
            1
            - math.cos(alpha_rad) ** 2
            - math.cos(beta_rad) ** 2
            - math.cos(gamma_rad) ** 2
            + 2
            * math.cos(alpha_rad)
            * math.cos(beta_rad)
            * math.cos(gamma_rad)
        )

        return (
            self.a
            * self.b
            * self.c
            * math.sqrt(volume_factor)
        )

    def as_tuple(self) -> tuple[float, float, float, float, float, float]:
        """Return the six unit-cell parameters as a tuple."""

        return (
            self.a,
            self.b,
            self.c,
            self.alpha,
            self.beta,
            self.gamma,
        )

    def is_valid(self) -> bool:
        """Basic validation of unit-cell parameters."""

        values = self.as_tuple()

        if any(value is None for value in values):
            return False

        if any(value <= 0 for value in (self.a, self.b, self.c)):
            return False

        if not (
            0 < self.alpha < 180
            and 0 < self.beta < 180
            and 0 < self.gamma < 180
        ):
            return False

        return True


   
@dataclass
class CAPDomain:
    domain_number: int
    unit_cell: UnitCell | None = None
    reduced_unit_cell: UnitCell | None = None
    cluster: str | None = None
    indexed_reflections: int | None = None
    total_reflections: int | None = None
    indexing_percent: float | None = None


@dataclass
class CAPResult:
    """Parsed result from a CrysAlisPro indexing operation."""

    success: bool

    domains: list[CAPDomain] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

@dataclass
class Dataset:
    """
    Represents one crystallographic dataset/folder.
    """

    name: str
    folder: Path

    # Filesystem information
    rodhypix_file: Path | None = None
    modification_date: datetime | None = None
    folder_size_mb: float | None = None

    # Existing crystallographic files
    ins_file: Path | None = None

    # Unit-cell information
    unit_cell: UnitCell | None = None
    unit_cell_source: str | None = None

    # CAP results
    cap_result: CAPResult | None = None

    # CCDC results
    ccdc_result: dict[str, Any] | None = None

    # Clustering
    cluster: str | None = None

    # Additional results that we may add later
    results: dict[str, Any] = field(default_factory=dict)