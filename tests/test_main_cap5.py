from pathlib import Path

from cap.connection import CAPConnection
from cap.indexing import run_indexing


PAR_FILE = Path(
    r"path/to/data/RA3-Cl-Bn/pre_RA3-Cl-Bn.par"
)


def main():

    print("=" * 60)
    print("CAP INDEXING TEST")
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

        print()
        print("Loading experiment:")
        print(PAR_FILE)

        load_result = connection.load_experiment(
            PAR_FILE
        )

        print()
        print("Load result:")
        print(load_result)

        print()
        print("-" * 60)
        print("RUNNING INDEXING")
        print("-" * 60)

        results = run_indexing(
            connection
        )

        print()
        print("Peak hunting result:")
        print(results["peak_hunting"])

        print()
        print("Unit-cell finding result:")
        print(results["unit_cell_finding"])

    finally:

        print()
        print("-" * 60)
        print("DISCONNECTING")
        print("-" * 60)

        connection.disconnect()

    print()
    print("Finished.")


if __name__ == "__main__":
    main()