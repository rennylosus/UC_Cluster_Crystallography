from pathlib import Path
from typing import Any

from config import CAP_ENABLED, DEBUG, DEBUG_CAP

from cap_auto.cap_control import CAPInstance


def debug_print(message: str) -> None:
    """Print a debug message when CAP debugging is enabled."""

    if DEBUG and DEBUG_CAP:
        print(message)


class CAPConnection:
    """
    Project-level wrapper around cap-auto.CAPInstance.

    A CAPConnection represents one CrysAlisPro session.

    Two workflows are supported:

    1. Start CAP with an experiment:
        CAPConnection(par_file=...)

    2. Start CAP without an experiment and load one later:
        CAPConnection()
        connection.connect()
        connection.load_experiment(...)
    """

    def __init__(
        self,
        par_file: Path | str | None = None,
        start_now: bool = True,
        raise_on_error: bool = False,
        min_cap_version: str | None = None,
        max_cap_version: str | None = None,
    ) -> None:

        self.enabled = CAP_ENABLED

        self.par_file = (
            Path(par_file)
            if par_file is not None
            else None
        )

        self.start_now = start_now
        self.raise_on_error = raise_on_error

        self.min_cap_version = min_cap_version
        self.max_cap_version = max_cap_version

        self.session: CAPInstance | None = None

    def connect(self) -> bool:
        """
        Start CrysAlisPro.

        If par_file was provided, it is passed to CAPInstance.

        If par_file is None, CrysAlisPro is started in listen
        mode without loading an experiment.
        """

        if not self.enabled:
            debug_print(
                "  CAP automation is disabled."
            )
            return False

        # ----------------------------------------------------
        # Validate experiment only if one was supplied
        # ----------------------------------------------------

        if self.par_file is not None:

            if not self.par_file.exists():

                raise FileNotFoundError(
                    "Experiment file does not exist: "
                    f"{self.par_file}"
                )

            debug_print(
                "  Starting CrysAlisPro with: "
                f"{self.par_file}"
            )

        else:

            debug_print(
                "  Starting CrysAlisPro "
                "in listen mode without an experiment."
            )

        # ----------------------------------------------------
        # Build CAPInstance arguments
        # ----------------------------------------------------

        cap_kwargs: dict[str, Any] = {
            "start_now": self.start_now,
            "raise_on_error": self.raise_on_error,
        }

        # Only pass par_file when one was supplied.
        if self.par_file is not None:

            cap_kwargs["par_file"] = (
                str(self.par_file)
            )

        # Only pass version restrictions when explicitly
        # configured. Otherwise cap-auto uses its defaults.
        if self.min_cap_version is not None:

            cap_kwargs["min_cap_version"] = (
                self.min_cap_version
            )

        if self.max_cap_version is not None:

            cap_kwargs["max_cap_version"] = (
                self.max_cap_version
            )

        # ----------------------------------------------------
        # Start CAP
        # ----------------------------------------------------

        try:

            self.session = CAPInstance(
                **cap_kwargs
            )

        except Exception as exc:

            print(
                "WARNING: Could not start "
                f"CrysAlisPro: {exc}"
            )

            self.session = None

            return False

        debug_print(
            "  CrysAlisPro started successfully."
        )

        return True

    def load_experiment(
        self,
        par_file: Path | str,
    ) -> Any:
        """
        Load a CrysAlisPro experiment into an already-running
        CAP session.

        This uses cap-auto's load_experiment() method.
        """

        if self.session is None:

            raise RuntimeError(
                "CrysAlisPro is not connected."
            )

        par_file = Path(par_file)

        if not par_file.exists():

            raise FileNotFoundError(
                "Experiment file does not exist: "
                f"{par_file}"
            )

        debug_print(
            "  Loading experiment: "
            f"{par_file}"
        )

        result = self.session.load_experiment(
            str(par_file)
        )

        debug_print(
            "  Experiment load completed."
        )

        return result

    def execute(
        self,
        command: str,
        timeout: float | None = None,
    ) -> Any:
        """
        Execute one CrysAlisPro command.
        """

        if self.session is None:

            raise RuntimeError(
                "CrysAlisPro is not connected."
            )

        debug_print(
            f"  CAP command: {command}"
        )

        if timeout is None:

            return self.session.execute(
                command
            )

        return self.session.execute(
            command,
            timeout=timeout,
        )

    def execute_batch(
        self,
        commands: list[str],
        timeout: float | None = None,
    ) -> Any:
        """
        Execute multiple CrysAlisPro commands.
        """

        if self.session is None:

            raise RuntimeError(
                "CrysAlisPro is not connected."
            )

        debug_print(
            f"  Executing {len(commands)} "
            "CAP commands."
        )

        if timeout is None:

            return self.session.execute_batch(
                commands
            )

        return self.session.execute_batch(
            commands,
            timeout=timeout,
        )

    def execute_macro(
        self,
        commands: list[str],
        timeout: float | None = None,
    ) -> Any:
        """
        Execute a sequence of CrysAlisPro commands
        as a macro.
        """

        if self.session is None:

            raise RuntimeError(
                "CrysAlisPro is not connected."
            )

        if timeout is None:

            return self.session.execute_macro(
                commands
            )

        return self.session.execute_macro(
            commands,
            timeout=timeout,
        )

    def get_status(self) -> Any:
        """Return the current CAP status."""

        if self.session is None:

            return None

        return self.session.get_status()

    @property
    def cap_version(self) -> Any:
        """Return the CrysAlisPro version."""

        if self.session is None:

            return None

        return self.session.cap_version

    @property
    def history(self) -> list[Any]:
        """Return the CAP command history."""

        if self.session is None:

            return []

        return self.session.history

    def disconnect(self) -> None:
        """Stop CrysAlisPro gracefully."""

        if self.session is None:

            return

        debug_print(
            "  Stopping CrysAlisPro..."
        )

        try:

            self.session.stop()

        except Exception as exc:

            print(
                "WARNING: Error while stopping "
                f"CrysAlisPro: {exc}"
            )

        finally:

            self.session = None

        debug_print(
            "  CrysAlisPro stopped."
        )


def find_par_file(
    dataset_folder: Path,
) -> Path | None:
    """
    Find the first CrysAlisPro .par file in a dataset folder.

    The search is recursive because the exact location of
    the experiment file may vary between datasets.
    """

    for file in dataset_folder.rglob("*.par"):

        if file.is_file():

            return file

    return None

