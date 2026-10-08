from pathlib import Path

from core.models import Dataset, UnitCell
from crystallography.clustering import (
    cluster_unit_cells,
    assign_clusters_to_datasets,
)


def make_dataset(name, cell):
    return Dataset(
        name=name,
        folder=Path(f"path/to/test/{name}"),
        unit_cell=cell,
    )


datasets = [
    # Should form cluster 1
    make_dataset(
        "RA3_001",
        UnitCell(
            10.000, 11.000, 12.000,
            90.0, 90.0, 90.0,
            source="TEST",
        ),
    ),

    # Within tolerance of RA3_001
    make_dataset(
        "RA3_002",
        UnitCell(
            10.015, 10.990, 12.010,
            90.1, 89.9, 90.0,
            source="TEST",
        ),
    ),

    # Outside tolerance -> new cluster
    make_dataset(
        "RA3_003",
        UnitCell(
            10.100, 11.000, 12.000,
            90.0, 90.0, 90.0,
            source="TEST",
        ),
    ),

    # Should form cluster 2 with RA3_003
    make_dataset(
        "RA3_004",
        UnitCell(
            10.110, 11.010, 11.990,
            90.1, 90.0, 89.9,
            source="TEST",
        ),
    ),

    # Different angle -> new cluster
    make_dataset(
        "RA3_005",
        UnitCell(
            10.000, 11.000, 12.000,
            90.5, 90.0, 90.0,
            source="TEST",
        ),
    ),
]


clusters = cluster_unit_cells(datasets)

assign_clusters_to_datasets(
    datasets,
    clusters,
)


print()
print("Clusters:")
for cluster in clusters:
    print(
        cluster.name,
        "->",
        [dataset.name for dataset in cluster.datasets],
    )

print()
print("Dataset assignments:")
for dataset in datasets:
    print(
        dataset.name,
        "->",
        dataset.cluster,
    )