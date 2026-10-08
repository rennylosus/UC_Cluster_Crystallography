from pathlib import Path


def find_par_file(
    dataset_folder: Path,
) -> Path | None:
    """
    Find the first CrysAlisPro .par file in a dataset folder.
    """

    for file in dataset_folder.rglob("*.par"):
        if file.is_file():
            return file

    return None
    
from config import (
    MAX_FOLDERS_TO_PROCESS,
    ROOT_DIRS,
)

from datasets.finder import (
    find_target_folders_multiple_roots,
)


folders = find_target_folders_multiple_roots(
    ROOT_DIRS
)

print()
print("=" * 70)
print("CAP EXPERIMENT FILE SEARCH")
print("=" * 70)

for folder in folders[:MAX_FOLDERS_TO_PROCESS]:

    par_file = find_par_file(folder)

    print()
    print(f"Dataset: {folder.name}")
    print(f"PAR:     {par_file}")