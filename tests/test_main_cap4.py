from pathlib import Path

from cap.connection import CAPConnection


# ------------------------------------------------------------
# Experiment
# ------------------------------------------------------------

PAR_FILE = Path(
    r"path/to/data/RA3-13do/pre_RA3-13do.par"
)


# ------------------------------------------------------------
# Main test
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("CAP EXPERIMENT LOAD + COMMAND TEST")
    print("=" * 60)

    print()
    print("Experiment:")
    print(PAR_FILE)

    # --------------------------------------------------------
    # Create connection
    # --------------------------------------------------------

    connection = CAPConnection(
        par_file=None,
        start_now=True,
        raise_on_error=False,
    )

    # --------------------------------------------------------
    # Start CrysAlisPro
    # --------------------------------------------------------

    print()
    print("Starting CrysAlisPro in listen mode...")

    connected = connection.connect()

    print()
    print("Connected:", connected)

    if not connected:
        print("ERROR: Could not connect to CrysAlisPro.")
        return

    try:

        # ----------------------------------------------------
        # CAP information
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("CAP INFORMATION")
        print("-" * 60)

        print("CAP version:")
        print(connection.cap_version)

        print("CAP status:")
        print(connection.get_status())

        print("Command history:")
        print(connection.history)

        # ----------------------------------------------------
        # Load experiment
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("LOADING EXPERIMENT")
        print("-" * 60)

        load_result = connection.load_experiment(
            PAR_FILE
        )

        print()
        print("Load result:")
        print(load_result)

        # ----------------------------------------------------
        # Test CAP communication after loading
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("CAP COMMUNICATION TEST")
        print("-" * 60)

        print()
        print("Sending:")
        print("xx sleep 1")

        result = connection.execute(
            "xx sleep 1"
        )

        print()
        print("Command result:")
        print(result)

        print()
        print("Success:")
        print(result.success)

        print()
        print("Warnings:")
        print(result.warnings)

        print()
        print("Errors:")
        print(result.errors)

        # ----------------------------------------------------
        # Final status
        # ----------------------------------------------------

        print()
        print("-" * 60)
        print("FINAL CAP STATUS")
        print("-" * 60)

        print("Status:")
        print(connection.get_status())

        print()
        print("Command history:")
        print(connection.history)

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

    print()
    print("=" * 60)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    main()