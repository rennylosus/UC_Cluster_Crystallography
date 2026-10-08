from __future__ import annotations

from datetime import datetime
from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import run_indexing
from config import (
    CAP_ENABLED,
    CAP_PAR_PREFIX_PREFERENCE,
    DEBUG,
    DEBUG_CAP,
)
from core.models import Dataset
from crystallography.clustering import ClusterManager
from crystallography.unit_cell import reduce_cells
from datasets.cell_reader import read_unit_cell
from datasets.ins_reader import find_ins_file
from datasets.metadata import get_folder_size
from datasets.rodhypix import find_first_rodhypix


def debug_print(message: str) -> None:
    if DEBUG:
        print(message)


def process_dataset(
    folder: Path,
    cap_connection: CAPConnection | None = None,
    cluster_manager: ClusterManager | None = None,
) -> Dataset:
    dataset = Dataset(
        name=folder.name,
        folder=folder,
    )

    dataset.rodhypix_file = find_first_rodhypix(folder)

    if dataset.rodhypix_file is not None:
        try:
            dataset.modification_date = datetime.fromtimestamp(
                dataset.rodhypix_file.stat().st_mtime
            )
        except Exception as exc:
            print(
                f"WARNING: Could not obtain modification date "
                f"for {dataset.name}: {exc}"
            )

    dataset.folder_size_mb = get_folder_size(folder)

    dataset.ins_file = find_ins_file(folder)
    dataset.unit_cell = read_unit_cell(dataset.ins_file)
    dataset.unit_cell_source = (
        "INS" if dataset.unit_cell is not None else None
    )

    if dataset.unit_cell is not None:
        debug_print(
            f"  INS-UC: {dataset.unit_cell.as_tuple()}"
        )

    if CAP_ENABLED:
        _process_cap(
            dataset,
            cap_connection=cap_connection,
            cluster_manager=cluster_manager,
        )

    return dataset


def _process_cap(
    dataset: Dataset,
    cap_connection: CAPConnection | None = None,
    cluster_manager: ClusterManager | None = None,
) -> None:
    par_file = _find_par_file(dataset.folder)

    if par_file is None:
        print(
            f"WARNING: No suitable .par file found "
            f"for {dataset.name}"
        )
        return

    owns_connection = False

    if cap_connection is None:
        connection = CAPConnection()
        owns_connection = True

        if not connection.connect():
            print(
                f"WARNING: Could not connect to CAP "
                f"for {dataset.name}"
            )
            return
    else:
        connection = cap_connection

        if connection.session is None:
            print(
                f"WARNING: Supplied CAP connection is "
                f"not connected for {dataset.name}"
            )
            return

    try:
        if DEBUG_CAP:
            print(
                f"  CAP .par selected: {par_file.name}"
            )

        connection.load_experiment(par_file)

        results = run_indexing(connection)
        dataset.cap_result = results["parsed_result"]

        if dataset.cap_result is None:
            print(
                f"WARNING: CAP returned no parsed result "
                f"for {dataset.name}"
            )
            return

        domains = [
            domain
            for domain in dataset.cap_result.domains
            if domain.unit_cell is not None
        ]

        debug_print(
            f"  CAP domains: {len(domains)}"
        )

        if not domains:
            return

        cap_cells = [
            domain.unit_cell
            for domain in domains
        ]

        reduced_cells = reduce_cells(cap_cells)

        for domain, reduced_cell in zip(
            domains,
            reduced_cells,
        ):
            domain.reduced_unit_cell = reduced_cell

            if cluster_manager is not None:
                domain.cluster = cluster_manager.assign(
                    reduced_cell
                )

            if DEBUG_CAP:
                print(
                    f"    Domain {domain.domain_number}:"
                )
                print(
                    f"      CAP-UC: "
                    f"{domain.unit_cell.as_tuple()}"
                )
                print(
                    f"      Gemmi-UC: "
                    f"{reduced_cell.as_tuple()}"
                )
                print(
                    f"      Indexed: "
                    f"{domain.indexed_reflections}"
                )
                print(
                    f"      Total: "
                    f"{domain.total_reflections}"
                )
                print(
                    f"      Indexing: "
                    f"{domain.indexing_percent}%"
                )
                print(
                    f"      Cluster: "
                    f"{domain.cluster}"
                )

    except Exception as exc:
        print(
            f"WARNING: CAP processing failed for "
            f"{dataset.name}: {exc}"
        )

    finally:
        if owns_connection:
            connection.disconnect()


def _find_par_file(
    dataset_folder: Path,
) -> Path | None:
    """
    Find the CAP .par file using the configured prefix preference.

    For a dataset named RA3-13do, for example:

        RA3-13do.par
        wit_RA3-13do.par
        pre_RA3-13do.par

    the order is controlled by CAP_PAR_PREFIX_PREFERENCE
    in config.py.
    """
    dataset_name = dataset_folder.name

    candidates: dict[str, Path] = {}

    for file in dataset_folder.rglob("*.par"):
        if not file.is_file():
            continue

        for prefix in CAP_PAR_PREFIX_PREFERENCE:
            expected_name = (
                f"{prefix}{dataset_name}.par"
            )

            if file.name.lower() == expected_name.lower():
                candidates[prefix] = file
                break

    for prefix in CAP_PAR_PREFIX_PREFERENCE:
        if prefix not in candidates:
            continue

        selected = candidates[prefix]

        if DEBUG_CAP:
            print(
                f"  .par candidate selected: "
                f"{selected.name}"
            )

            ignored = [
                path.name
                for other_prefix, path in candidates.items()
                if other_prefix != prefix
            ]

            if ignored:
                print(
                    f"  .par candidates ignored: "
                    f"{', '.join(sorted(ignored))}"
                )

        return selected

    return None


__all__ = [
    "process_dataset",
]
