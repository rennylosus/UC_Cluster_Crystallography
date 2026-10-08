from config import (
    MAX_FOLDERS_TO_PROCESS,
    ROOT_DIRS,
    LENGTH_TOLERANCE,
    ANGLE_TOLERANCE,
)

from core.models import Dataset
from datasets.finder import find_target_folders_multiple_roots
from datasets.rodhypix import (
    find_first_rodhypix,
    get_rodhypix_modification_date,
)
from datasets.metadata import get_folder_size
from datasets.ins_reader import (
    find_ins_file,
    extract_unit_cell,
)

from crystallography.unit_cell import reduce_cell
from crystallography.clustering import (
    cluster_unit_cells,
    assign_clusters_to_datasets,
)


# ============================================================
# 1. FIND DATASETS
# ============================================================

folders = find_target_folders_multiple_roots(
    ROOT_DIRS
)

folders = folders[:MAX_FOLDERS_TO_PROCESS]


# ============================================================
# 2. BUILD DATASET OBJECTS
# ============================================================

datasets = []

for folder in folders:

    dataset = Dataset(
        name=folder.name,
        folder=folder,
    )

    dataset.rodhypix_file = (
        find_first_rodhypix(folder)
    )

    dataset.modification_date = (
        get_rodhypix_modification_date(
            dataset.rodhypix_file
        )
    )

    dataset.folder_size_mb = (
        get_folder_size(folder)
    )

    dataset.ins_file = (
        find_ins_file(folder)
    )

    dataset.unit_cell = (
        extract_unit_cell(
            dataset.ins_file
        )
    )

    if dataset.unit_cell is not None:
        dataset.unit_cell_source = "INS"

    datasets.append(dataset)


# ============================================================
# 3. REDUCE UNIT CELLS
# ============================================================

print()
print("=" * 80)
print("UNIT-CELL REDUCTION")
print("=" * 80)

for dataset in datasets:

    if dataset.unit_cell is None:
        print()
        print(f"{dataset.name}: no unit cell")
        continue

    original_cell = dataset.unit_cell

    print()
    print(f"Dataset: {dataset.name}")

    print(
        "  Original: "
        f"a={original_cell.a:.6f}, "
        f"b={original_cell.b:.6f}, "
        f"c={original_cell.c:.6f}, "
        f"α={original_cell.alpha:.3f}, "
        f"β={original_cell.beta:.3f}, "
        f"γ={original_cell.gamma:.3f}"
    )

    print(
        f"  Original volume: "
        f"{original_cell.volume:.6f} Å³"
    )

    reduced_cell = reduce_cell(
        original_cell,
        method="niggli",
    )

    print(
        "  Niggli:   "
        f"a={reduced_cell.a:.6f}, "
        f"b={reduced_cell.b:.6f}, "
        f"c={reduced_cell.c:.6f}, "
        f"α={reduced_cell.alpha:.3f}, "
        f"β={reduced_cell.beta:.3f}, "
        f"γ={reduced_cell.gamma:.3f}"
    )

    print(
        f"  Reduced volume: "
        f"{reduced_cell.volume:.6f} Å³"
    )

    volume_difference = (
        reduced_cell.volume
        - original_cell.volume
    )

    print(
        f"  Volume difference: "
        f"{volume_difference:.12f} Å³"
    )

    dataset.unit_cell = reduced_cell
    dataset.unit_cell_source = "INS + NIGGLI"


# ============================================================
# 4. CLUSTER
# ============================================================

clusters = cluster_unit_cells(
    datasets,
    length_tolerance=LENGTH_TOLERANCE,
    angle_tolerance=ANGLE_TOLERANCE,
)

assign_clusters_to_datasets(
    datasets,
    clusters,
)


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

print()
print("=" * 80)
print("PRE-CAP CRYSTALLOGRAPHY PIPELINE")
print("=" * 80)

print()
print(
    f"Datasets processed: {len(datasets)}"
)

print(
    f"Clusters found:     {len(clusters)}"
)

print()
print("-" * 80)
print("DATASETS")
print("-" * 80)

for dataset in datasets:

    print()
    print(f"Dataset: {dataset.name}")
    print(f"Phase:   {dataset.cluster}")

    if dataset.unit_cell is None:
        print("Cell:    None")
        continue

    cell = dataset.unit_cell

    print(
        "Cell:    "
        f"a={cell.a:.4f}, "
        f"b={cell.b:.4f}, "
        f"c={cell.c:.4f}, "
        f"α={cell.alpha:.3f}, "
        f"β={cell.beta:.3f}, "
        f"γ={cell.gamma:.3f}"
    )

    print(
        f"Volume:  {cell.volume:.3f} Å³"
    )


print()
print("-" * 80)
print("CLUSTERS")
print("-" * 80)

for cluster in clusters:

    print()
    print(
        f"{cluster.name}: "
        f"{len(cluster.datasets)} dataset(s)"
    )

    for dataset in cluster.datasets:
        print(
            f"  - {dataset.name}"
        )