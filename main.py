from __future__ import annotations

from pathlib import Path

from cap.connection import CAPConnection
from config import (
    CAP_ENABLED,
    MAX_FOLDERS_TO_PROCESS,
    OUTPUT_DIR,
    OUTPUT_PREFIX,
    ROOT_DIRS,
)
from crystallography.clustering import ClusterManager
from datasets.finder import find_target_folders
from datasets.processor import process_dataset
from output.html import write_html_report
from output.excel import write_excel_report


def main() -> None:
    print("=" * 70)
    print("RA3 CRYSTALLOGRAPHIC DATASET PROCESSING")
    print("=" * 70)

    # ---------------------------------------------------------
    # FIND MATCHING FOLDERS ACROSS ALL ROOTS
    # ---------------------------------------------------------

    all_folders = []

    for root_dir in ROOT_DIRS:
        print()
        print(f"Searching root directory: {root_dir}")

        if not root_dir.is_dir():
            print(
                "WARNING: Root directory does not exist "
                f"or is not accessible: {root_dir}"
            )
            continue

        found_folders = find_target_folders(root_dir)

        print(
            f"Found {len(found_folders)} matching folder(s)"
        )

        all_folders.extend(found_folders)

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    target_folders = sorted(set(all_folders))

    print()
    print(
        f"Total matching folders: "
        f"{len(target_folders)}"
    )

    if not target_folders:
        print()
        print("No matching folders found.")
        return

    # ---------------------------------------------------------
    # APPLY PROCESSING LIMIT
    # ---------------------------------------------------------

    if MAX_FOLDERS_TO_PROCESS is not None:
        target_folders = target_folders[
            :MAX_FOLDERS_TO_PROCESS
        ]

        print(
            f"Processing first "
            f"{len(target_folders)} folder(s) "
            f"because MAX_FOLDERS_TO_PROCESS = "
            f"{MAX_FOLDERS_TO_PROCESS}"
        )

    else:
        print(
            f"Processing all "
            f"{len(target_folders)} matching folders."
        )

    # ---------------------------------------------------------
    # GLOBAL CLUSTER MANAGER
    # ---------------------------------------------------------
    #
    # A single manager is used for the entire run.
    #
    # Each CAP domain is:
    #
    #     CAP-UC
    #       ↓
    #     Gemmi reduction
    #       ↓
    #     immediate global cluster assignment
    #
    # Therefore there is NO final clustering pass.
    # ---------------------------------------------------------

    cluster_manager = ClusterManager()

    # ---------------------------------------------------------
    # DATASET STORAGE
    # ---------------------------------------------------------

    datasets = []

    # ---------------------------------------------------------
    # HTML LIVE REPORT
    # ---------------------------------------------------------

    html_file = (
        OUTPUT_DIR
        / f"{OUTPUT_PREFIX}.html"
    )

    print()
    print(
        f"Live HTML report: {html_file}"
    )

    # Create initial empty report.
    write_html_report(
        datasets=datasets,
        output_file=html_file,
        total_datasets=len(target_folders),
        processing_complete=False,
    )

    # ---------------------------------------------------------
    # START ONE PERSISTENT CAP SESSION
    # ---------------------------------------------------------

    cap_connection = None

    if CAP_ENABLED:
        print()
        print("-" * 70)
        print(
            "Starting CrysAlisPro "
            "for persistent CAP session"
        )
        print("-" * 70)

        cap_connection = CAPConnection(
            par_file=None,
            start_now=True,
            raise_on_error=False,
        )

        if not cap_connection.connect():
            print(
                "WARNING: Could not start "
                "persistent CrysAlisPro session."
            )
            print(
                "CAP processing will be skipped."
            )
            cap_connection = None

        else:
            print(
                "CrysAlisPro started. "
                "The same session will be reused "
                "for all datasets."
            )

    # ---------------------------------------------------------
    # PROCESS DATASETS
    # ---------------------------------------------------------

    try:
        for index, folder in enumerate(
            target_folders,
            start=1,
        ):
            print()
            print("-" * 70)
            print(
                f"Dataset {index}/"
                f"{len(target_folders)}: "
                f"{folder.name}"
            )
            print("-" * 70)

            try:
                dataset = process_dataset(
                    folder,
                    cap_connection=cap_connection,
                    cluster_manager=cluster_manager,
                )

                datasets.append(dataset)

                print()
                print(
                    f"Dataset: {dataset.name}"
                )

                print(
                    f"INS-UC: "
                    f"{dataset.unit_cell}"
                )

                if dataset.cap_result is None:
                    print(
                        "CAP: no result"
                    )

                else:
                    print(
                        "CAP domains: "
                        f"{len(dataset.cap_result.domains)}"
                    )

                    for domain in (
                        dataset.cap_result.domains
                    ):
                        print(
                            f"  Domain "
                            f"{domain.domain_number}:"
                        )

                        print(
                            f"    CAP-UC: "
                            f"{domain.unit_cell}"
                        )

                        print(
                            f"    Gemmi-UC: "
                            f"{domain.reduced_unit_cell}"
                        )

                        print(
                            f"    Indexing: "
                            f"{domain.indexing_percent}"
                        )

                        print(
                            f"    Cluster: "
                            f"{domain.cluster if domain.cluster is not None else '—'}"
                        )

            except Exception as exc:
                print(
                    "WARNING: Dataset processing "
                    f"failed for {folder}: {exc}"
                )

            # -------------------------------------------------
            # UPDATE HTML AFTER EVERY DATASET
            # -------------------------------------------------
            #
            # Clustering has already happened inside
            # process_dataset(), immediately after Gemmi
            # reduction.
            #
            # This call only writes the current state.
            # It does NOT perform clustering.
            # -------------------------------------------------

            write_html_report(
                datasets=datasets,
                output_file=html_file,
                total_datasets=len(target_folders),
                processing_complete=False,
            )

            print(
                f"HTML report updated: {html_file}"
            )

    finally:
        # -----------------------------------------------------
        # STOP ONE PERSISTENT CAP SESSION
        # -----------------------------------------------------

        if cap_connection is not None:
            print()
            print("-" * 70)
            print(
                "Stopping persistent "
                "CrysAlisPro session"
            )
            print("-" * 70)

            cap_connection.disconnect()

    # ---------------------------------------------------------
    # FINAL HTML REPORT
    # ---------------------------------------------------------

    write_html_report(
        datasets=datasets,
        output_file=html_file,
        total_datasets=len(target_folders),
        processing_complete=True,
    )

    excel_file = write_excel_report(datasets)

    print(
        f"Excel report:\n"
        f"{excel_file}"
        )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        f"Datasets processed: "
        f"{len(datasets)}/{len(target_folders)}"
    )

    print(
        f"Global clusters: "
        f"{cluster_manager.count}"
    )

    print(
        f"HTML report:\n"
        f"{html_file}"
    )

    print()
    print("Clusters:")

    for cluster in cluster_manager.clusters:
        print(
            f"  {cluster.name}: "
            f"{len(cluster.cells)} cell(s)"
        )


if __name__ == "__main__":
    main()
