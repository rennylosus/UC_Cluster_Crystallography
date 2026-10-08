from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import (
    get_indexed_unit_cells,
    run_indexing,
)
from crystallography.clustering import cluster_reduced_cells
from crystallography.unit_cell import reduce_cells
from cap.indexing import get_indexed_domains


PAR_FILE = Path(
    r"path/to/data/RA3-13do/pre_RA3-13do.par"
)


def main() -> None:
    print("=== CAP CONNECTION TEST ===")

    connection = CAPConnection(
        par_file=None,
        start_now=True,
        raise_on_error=False,
    )

    if not connection.connect():
        print("ERROR: Could not connect to CrysAlisPro.")
        return

    try:
        print()
        print("CAP version:", connection.cap_version)

        # ---------------------------------------------------------
        # Load experiment
        # ---------------------------------------------------------
        print()
        print("=== LOADING EXPERIMENT ===")

        connection.load_experiment(PAR_FILE)

        # ---------------------------------------------------------
        # Run CAP indexing
        # ---------------------------------------------------------
        print()
        print("=== RUNNING CAP INDEXING ===")

        results = run_indexing(connection)

        # ---------------------------------------------------------
        # Parsed CAP result
        # ---------------------------------------------------------
        print()
        print("=== PARSED CAP RESULT ===")

        parsed_result = results["parsed_result"]

        if parsed_result is None:
            print("No parsed CAP result.")
            return

        print("Success:", parsed_result.success)
        print("Errors:", parsed_result.errors)
        print("Warnings:", parsed_result.warnings)
        print("Domains:", len(parsed_result.domains))

        for domain in parsed_result.domains:
            print()
            print(f"Domain {domain.domain_number}")

            if domain.unit_cell is not None:
                print("  Cell:", domain.unit_cell.as_tuple())
                print("  Volume:", domain.unit_cell.volume)
            else:
                print("  Cell: None")

            print("  Indexed:", domain.indexed_reflections)
            print("  Total:", domain.total_reflections)
            print("  Indexing %:", domain.indexing_percent)

        # ---------------------------------------------------------
        # CAP → UnitCell
        # ---------------------------------------------------------
        print()
        print("=== CAP → UNIT CELLS ===")

        cells = get_indexed_unit_cells(results)

        print("Number of CAP cells:", len(cells))

        for index, cell in enumerate(cells, start=1):
            print()
            print(f"Domain {index} original:")
            print("  Cell:", cell.as_tuple())
            print("  Volume:", cell.volume)

        # ---------------------------------------------------------
        # UnitCell → Gemmi
        # ---------------------------------------------------------
        print()
        print("=== GEMMI REDUCTION ===")

        reduced_cells = reduce_cells(cells)

        print("Number of reduced cells:", len(reduced_cells))

        for index, cell in enumerate(reduced_cells, start=1):
            print()
            print(f"Domain {index} reduced:")
            print("  Cell:", cell.as_tuple())
            print("  Volume:", cell.volume)

        # ---------------------------------------------------------
        # Gemmi → Clustering
        # ---------------------------------------------------------
        print()
        print("=== CLUSTERING ===")

        clusters = cluster_reduced_cells(reduced_cells)

        print("Number of cluster assignments:", len(clusters))

        for index, cluster in enumerate(clusters, start=1):
            print(
                f"Domain {index} → {cluster}"
            )

    finally:
        # ---------------------------------------------------------
        # Disconnect
        # ---------------------------------------------------------
        print()
        print("=== DISCONNECTING ===")

        connection.disconnect()


if __name__ == "__main__":
    main()