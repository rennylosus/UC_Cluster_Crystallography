from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import run_indexing


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

        print()
        print("=== LOADING EXPERIMENT ===")
        connection.load_experiment(PAR_FILE)

        print()
        print("=== RUNNING CAP INDEXING ===")

        results = run_indexing(connection)

        # ---------------------------------------------------------
        # Raw Smart Peak Hunting result
        # ---------------------------------------------------------
        print()
        print("=== SMART PEAK HUNTING ===")

        peak_result = results["peak_hunting"]

        if peak_result is not None:
            print("Success:", peak_result.success)
            print("Log output:")
            print(peak_result.log_output)
        else:
            print("No peak-hunting result.")

        # ---------------------------------------------------------
        # Raw multicrystal indexing result
        # ---------------------------------------------------------
        print()
        print("=== RAW MULTICRYSTAL INDEXING ===")

        unit_cell_result = results["unit_cell_finding"]

        if unit_cell_result is not None:
            print("Success:", unit_cell_result.success)
            print("Log output:")
            print(unit_cell_result.log_output)
        else:
            print("No multicrystal indexing result.")

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

    finally:
        print()
        print("=== DISCONNECTING ===")
        connection.disconnect()


if __name__ == "__main__":
    main()