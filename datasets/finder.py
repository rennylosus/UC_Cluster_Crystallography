from pathlib import Path

from config import (
    CASE_SENSITIVE,
    DEBUG,
    DEBUG_SEARCH,
    SEARCH_RECURSION_DEPTH,
    SEARCH_STRING,
)


def debug_print(message: str) -> None:
    """Print a debug message if search debugging is enabled."""

    if DEBUG and DEBUG_SEARCH:
        print(message)


def matches_search_string(folder_name: str) -> bool:
    """
    Determine whether a folder name contains SEARCH_STRING.

    Matching can be case-sensitive or case-insensitive,
    according to config.py.
    """

    if CASE_SENSITIVE:
        return SEARCH_STRING in folder_name

    return SEARCH_STRING.lower() in folder_name.lower()


def find_target_folders(root: Path) -> list[Path]:
    """
    Find dataset folders below a root directory.

    Only directories are inspected during the search.

    SEARCH_RECURSION_DEPTH:
        0    -> do not inspect subdirectories
        1    -> inspect directories directly inside root
        2    -> search two levels down
        None -> unlimited recursion

    Once a matching dataset folder is found, its contents are
    not searched for additional matching dataset folders.
    """

    folders: list[Path] = []

    if not root.is_dir():
        return folders

    def scan(directory: Path, current_depth: int) -> None:

        debug_print(f"Searching: {directory}")

        try:
            entries = list(directory.iterdir())

        except (PermissionError, OSError) as exc:
            print(
                f"WARNING: Cannot access directory "
                f"{directory}: {exc}"
            )
            return

        for entry in entries:

            if not entry.is_dir():
                continue

            # ------------------------------------------------
            # Check whether this directory is a dataset
            # ------------------------------------------------

            if matches_search_string(entry.name):

                debug_print(
                    f"  MATCH: {entry}"
                )

                folders.append(entry)

                # Do not search inside a matching dataset.
                continue

            # ------------------------------------------------
            # Check recursion limit
            # ------------------------------------------------

            if (
                SEARCH_RECURSION_DEPTH is not None
                and current_depth >= SEARCH_RECURSION_DEPTH
            ):
                continue

            # ------------------------------------------------
            # Continue searching
            # ------------------------------------------------

            scan(
                entry,
                current_depth + 1,
            )

    scan(root, 0)

    return folders


def find_target_folders_multiple_roots(
    roots: list[Path],
) -> list[Path]:
    """
    Search multiple root directories and combine the results.

    Duplicate paths are removed.

    Invalid or inaccessible roots generate a warning but do
    not stop the search of other roots.
    """

    all_folders: list[Path] = []

    for root in roots:

        print()
        print(
            f"Searching root directory: {root}"
        )

        if not root.is_dir():

            print(
                "WARNING: Root directory does not exist "
                f"or is not accessible: {root}"
            )

            continue

        found = find_target_folders(root)

        print(
            f"Found {len(found)} matching folder(s) "
            f"in {root}"
        )

        all_folders.extend(found)

    # Remove duplicate paths and sort.
    unique_folders = sorted(
        set(all_folders)
    )

    print()
    print(
        "Total matching folders across all roots: "
        f"{len(unique_folders)}"
    )

    return unique_folders