from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import run_indexing
from cap.parser import parse_cap_result


PAR_FILE = Path(
    r"path/to/data/RA3-13do/pre_RA3-13do.par"
)


def main():

    print("=" * 60)
    print("CAP INDEXING + PARSER TEST")
    print("=" * 60)

    connection = CAPConnection(
        par_file=None,
        start_now=True,
        raise_on_error=False,
    )

    connected = connection.connect()

    print()
    print("Connected:", connected)

    if not connected:
        print("ERROR: Could not connect to CrysAlisPro.")
        return

    try:

        # ----------------------------------------------------
        # Load experiment
        # ----------------------------------------------------

        print()
        print("Loading experiment:")
        print(PAR_FILE)

        load_result = connection.load_experiment(
            PAR_FILE
        )

        print()
        print("Load result:")
        print(load_result)

        # ----------------------------------------------------
        # Run CAP indexing
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("RUNNING INDEXING")
        print("-" * 60)

        results = run_indexing(
            connection
        )

        # ----------------------------------------------------
        # Raw CAP results
        # ----------------------------------------------------

        print()
        print("Peak hunting result:")
        print(results["peak_hunting"])

        print()
        print("Unit-cell finding result:")
        print(results["unit_cell_finding"])

        # ----------------------------------------------------
        # Parse unit-cell result
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("PARSING CAP UNIT-CELL RESULT")
        print("-" * 60)

        unit_cell_result = results[
            "unit_cell_finding"
        ]

        parsed_result = parse_cap_result(
            log_output=unit_cell_result.log_output,
            success=unit_cell_result.success,
        )

        # ----------------------------------------------------
        # CAP result information
        # ----------------------------------------------------

        print()
        print("CAP success:")
        print(parsed_result.success)

        print()
        print("CAP errors:")
        print(parsed_result.errors)

        print()
        print("CAP warnings:")
        print(parsed_result.warnings)

        # ----------------------------------------------------
        # Domains
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("CAP DOMAINS")
        print("-" * 60)

        print()
        print("Number of domains:")
        print(len(parsed_result.domains))

        for domain in parsed_result.domains:

            print()
            print(
                f"Domain {domain.domain_number}"
            )

            # ----------------------------------------------
            # Unit cell
            # ----------------------------------------------

            print("  Unit cell:")

            if domain.unit_cell is None:

                print("    None")

            else:

                cell = domain.unit_cell

                print(
                    f"    a      = {cell.a}"
                )

                print(
                    f"    b      = {cell.b}"
                )

                print(
                    f"    c      = {cell.c}"
                )

                print(
                    f"    alpha  = {cell.alpha}"
                )

                print(
                    f"    beta   = {cell.beta}"
                )

                print(
                    f"    gamma  = {cell.gamma}"
                )

                print(
                    f"    volume = {cell.volume}"
                )

                print(
                    f"    source = {cell.source}"
                )

            # ----------------------------------------------
            # Indexing
            # ----------------------------------------------

            print()
            print("  Indexing:")

            print(
                "    Indexed reflections = "
                f"{domain.indexed_reflections}"
            )

            print(
                "    Total reflections   = "
                f"{domain.total_reflections}"
            )

            print(
                "    Indexing %           = "
                f"{domain.indexing_percent}"
            )

    finally:

        # ----------------------------------------------------
        # Disconnect
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("DISCONNECTING")
        print("-" * 60)

        connection.disconnect()

    print()
    print("Finished.")


if __name__ == "__main__":
    main()