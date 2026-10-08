from config import (
    MAX_FOLDERS_TO_PROCESS,
    ROOT_DIRS,
)
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
from core.models import Dataset


folders = find_target_folders_multiple_roots(ROOT_DIRS)

print()
print("=" * 70)
print("DATASET DETAILS")
print("=" * 70)

datasets = []

for folder in folders[:MAX_FOLDERS_TO_PROCESS]:

    print()
    print(f"Processing: {folder}")

    dataset = Dataset(
        name=folder.name,
        folder=folder,
    )

    # --------------------------------------------------------
    # RODHYPIX
    # --------------------------------------------------------

    dataset.rodhypix_file = find_first_rodhypix(
        folder
    )

    dataset.modification_date = (
        get_rodhypix_modification_date(
            dataset.rodhypix_file
        )
    )

    # --------------------------------------------------------
    # FOLDER SIZE
    # --------------------------------------------------------

    dataset.folder_size_mb = get_folder_size(
        folder
    )

    # --------------------------------------------------------
    # INS
    # --------------------------------------------------------

    dataset.ins_file = find_ins_file(
        folder
    )

    # --------------------------------------------------------
    # UNIT CELL
    # --------------------------------------------------------

    dataset.unit_cell = extract_unit_cell(
        dataset.ins_file
    )

    if dataset.unit_cell is not None:
        dataset.unit_cell_source = "INS"

    datasets.append(dataset)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

for dataset in datasets:

    print()
    print(f"Dataset: {dataset.name}")
    print(f"Folder:  {dataset.folder}")

    print(
        f"RODHYPIX: {dataset.rodhypix_file}"
    )

    print(
        f"Modified: {dataset.modification_date}"
    )

    print(
        f"Size:     {dataset.folder_size_mb:.2f} MB"
    )

    print(
        f"INS:      {dataset.ins_file}"
    )

    if dataset.unit_cell is not None:

        print(
            "Cell:     "
            f"{dataset.unit_cell.as_tuple()}"
        )

        print(
            f"Volume:   {dataset.unit_cell.volume:.3f} Å³"
        )

    else:

        print("Cell:     None")