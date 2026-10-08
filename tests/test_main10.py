from __future__ import annotations

from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import run_indexing
from config import ROOT_DIRS, SEARCH_STRING


def find_ra3_par_files() -> list[Path]:
    """
    Find .par files belonging to the first two RA3 datasets.
    """

    folders: list[Path] = []

    for root_dir in ROOT_DIRS:
        if not root_dir.is_dir():
            continue

        for folder in root_dir.iterdir():
            if not folder.is_dir():
                continue

            if SEARCH_STRING.lower() not in folder.name.lower():
                continue

            folders.append(folder)

    folders = sorted(folders)

    par_files: list[Path] = []

    for folder in folders:
        for par_file in folder.rglob("*.par"):
            if par_file.is_file():
                par_files.append(par_file)
                break

        if len(par_files) >= 2:
            break

    return par_files


def process_with_existing_cap(
    connection: CAPConnection,
    par_file: Path,
) -> None:
    """
    Load one experiment into an already-running CAP session
    and run the existing CAP indexing workflow.
    """

    print()
    print("=" * 70)
    print(f"DATASET: {par_file.parent.parent.name}")
    print(f"PAR FILE: {par_file}")
    print("=" * 70)

    print()
    print("Loading experiment...")

    connection.load_experiment(par_file)

    print("Experiment loaded.")

    print()
    print("Running CAP...")

    results = run_indexing(connection)

    print()
    print("CAP completed.")

    parsed_result = results.get("parsed_result")

    if parsed_result is None:
        print("No parsed CAP result.")
        return

    print()
    print(
        f"CAP success: {parsed_result.success}"
    )

    print(
        f"Domains found: "
        f"{len(parsed_result.domains)}"
    )

    for domain in parsed_result.domains:

        print()
        print(
            f"Domain {domain.domain_number}"
        )

        if domain.unit_cell is not None:
            print(
                "  Unit cell: "
                f"{domain.unit_cell.as_tuple()}"
            )

        if domain.indexing_percent is not None:
            print(
                "  Indexing: "
                f"{domain.indexing_percent:.2f}%"
            )

    if parsed_result.errors:

        print()
        print("CAP errors:")

        for error in parsed_result.errors:
            print(
                f"  - {error}"
            )

    if parsed_result.warnings:

        print()
        print("CAP warnings:")

        for warning in parsed_result.warnings:
            print(
                f"  - {warning}"
            )


def main() -> None:

    print("=" * 70)
    print("PERSISTENT CAP SESSION TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Find two datasets
    # ---------------------------------------------------------

    par_files = find_ra3_par_files()

    print()
    print(
        f"Found {len(par_files)} suitable .par file(s)."
    )

    if len(par_files) < 2:
        print(
            "ERROR: Need at least two RA3 datasets "
            "with .par files."
        )
        return

    print()

    for index, par_file in enumerate(
        par_files,
        start=1,
    ):
        print(
            f"{index}. {par_file}"
        )

    # ---------------------------------------------------------
    # Start CAP ONCE
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("Starting CrysAlisPro ONCE")
    print("-" * 70)

    connection = CAPConnection(
        par_file=None,
        start_now=True,
        raise_on_error=False,
    )

    if not connection.connect():
        print(
            "ERROR: Could not connect to CrysAlisPro."
        )
        return

    print()
    print(
        "CrysAlisPro is running."
    )

    try:

        # -----------------------------------------------------
        # Dataset 1
        # -----------------------------------------------------

        process_with_existing_cap(
            connection,
            par_files[0],
        )

        # -----------------------------------------------------
        # Dataset 2
        # -----------------------------------------------------

        print()
        print("-" * 70)
        print(
            "Reusing the SAME CrysAlisPro session "
            "for dataset 2"
        )
        print("-" * 70)

        process_with_existing_cap(
            connection,
            par_files[1],
        )

        # -----------------------------------------------------
        # Finished
        # -----------------------------------------------------

        print()
        print("=" * 70)
        print("BOTH DATASETS PROCESSED")
        print("The CAP session was kept open between them.")
        print("=" * 70)

    except Exception as exc:

        print()
        print(
            "ERROR during persistent CAP test:"
        )
        print(
            f"  {exc}"
        )

    finally:

        # -----------------------------------------------------
        # Stop CAP ONCE
        # -----------------------------------------------------

        print()
        print("-" * 70)
        print("Stopping CrysAlisPro")
        print("-" * 70)

        connection.disconnect()


if __name__ == "__main__":
    main()