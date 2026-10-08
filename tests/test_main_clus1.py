from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import (
    get_indexed_domains,
    run_indexing,
)
from crystallography.clustering import cluster_reduced_cells
from crystallography.unit_cell import reduce_cells


PAR_FILE = Path(
    r"path/to/data/.par"
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
        # Get CAP domains
        # ---------------------------------------------------------
        print()
        print("=== CAP DOMAINS ===")

        domains = get_indexed_domains(results)

        print("Number of indexed domains:", len(domains))

        for domain_number, cell in domains:
            print()
            print(f"Domain {domain_number}")
            print("  CAP-UC:", cell.as_tuple())
            print("  CAP volume:", cell.volume)

        # ---------------------------------------------------------
        # Extract CAP unit cells
        # ---------------------------------------------------------
        cap_cells = [
            cell
            for domain_number, cell in domains
        ]

        # ---------------------------------------------------------
        # Gemmi reduction
        # ---------------------------------------------------------
        print()
        print("=== GEMMI REDUCTION ===")

        gemmi_cells = reduce_cells(cap_cells)

        print("Number of reduced cells:", len(gemmi_cells))

        for (domain_number, _), cell in zip(
            domains,
            gemmi_cells,
        ):
            print()
            print(f"Domain {domain_number}")
            print("  Gemmi-UC:", cell.as_tuple())
            print("  Gemmi volume:", cell.volume)

        # ---------------------------------------------------------
        # Clustering
        # ---------------------------------------------------------
        print()
        print("=== CLUSTERING ===")

        clusters = cluster_reduced_cells(gemmi_cells)

        print(
            "Number of cluster assignments:",
            len(clusters),
        )

        for (domain_number, _), cluster in zip(
            domains,
            clusters,
        ):
            print(
                f"Domain {domain_number} → {cluster}"
            )

        # ---------------------------------------------------------
        # Final aligned representation
        # ---------------------------------------------------------
        print()
        print("=== CAP → GEMMI → CLUSTER ===")

        for (
            (domain_number, cap_cell),
            gemmi_cell,
            cluster,
        ) in zip(
            domains,
            gemmi_cells,
            clusters,
        ):
            print()
            print(f"Domain {domain_number}")
            print("  CAP-UC:")
            print("   ", cap_cell.as_tuple())
            print("  Gemmi-UC:")
            print("   ", gemmi_cell.as_tuple())
            print("  Cluster:", cluster)

    finally:
        # ---------------------------------------------------------
        # Disconnect
        # ---------------------------------------------------------
        print()
        print("=== DISCONNECTING ===")

        connection.disconnect()


if __name__ == "__main__":
    main()