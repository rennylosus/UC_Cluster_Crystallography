from typing import Any

from cap.connection import CAPConnection
from cap.parser import parse_cap_result
from config import (
    CAP_PEAK_FINDING,
    CAP_MULTICRYSTAL_INDEXING,
    DEBUG,
    DEBUG_CAP,
    TWIN_MULTICRYSTAL_INDEXING_COMMAND,
    SMART_PEAK_HUNTING_COMMAND
)
from core.models import UnitCell


SMART_PEAK_HUNTING_COMMAND = SMART_PEAK_HUNTING_COMMAND

TWIN_MULTICRYSTAL_INDEXING_COMMAND = TWIN_MULTICRYSTAL_INDEXING_COMMAND


def debug_print(message: str) -> None:
    if DEBUG and DEBUG_CAP:
        print(message)


def run_peak_hunting(connection: CAPConnection) -> Any:
    if not CAP_PEAK_FINDING:
        debug_print("  CAP peak finding is disabled.")
        return None

    debug_print("  Running Smart Peak Hunting...")
    result = connection.execute(SMART_PEAK_HUNTING_COMMAND)
    debug_print("  Smart Peak Hunting completed.")

    return result


def run_multicrystal_indexing(connection: CAPConnection) -> Any:
    if not CAP_MULTICRYSTAL_INDEXING:
        debug_print("  CAP multicrystal indexing is disabled.")
        return None

    debug_print(
        "  Running twin/multicrystal unit-cell finding..."
    )

    result = connection.execute(
        TWIN_MULTICRYSTAL_INDEXING_COMMAND
    )

    debug_print(
        "  Twin/multicrystal unit-cell finding completed."
    )

    return result


def run_indexing(
    connection: CAPConnection,
) -> dict[str, Any]:
    debug_print("  Starting CAP indexing workflow.")

    peak_result = run_peak_hunting(connection)

    unit_cell_result = run_multicrystal_indexing(
        connection
    )

    parsed_result = None

    if unit_cell_result is not None:
        parsed_result = parse_cap_result(
            log_output=unit_cell_result.log_output,
            success=unit_cell_result.success,
        )

    debug_print("  CAP indexing workflow completed.")

    return {
        "peak_hunting": peak_result,
        "unit_cell_finding": unit_cell_result,
        "parsed_result": parsed_result,
    }


def get_indexed_unit_cells(
    results: dict[str, Any],
) -> list[UnitCell]:
    """
    Return all successfully indexed CAP domain unit cells.

    Each CAP domain is kept as a separate unit cell.
    """

    parsed_result = results.get("parsed_result")

    if parsed_result is None:
        return []

    cells: list[UnitCell] = []

    for domain in parsed_result.domains:
        if domain.unit_cell is not None:
            cells.append(domain.unit_cell)

    return cells


def get_indexed_domains(
    results: dict[str, Any],
) -> list[tuple[int, UnitCell]]:
    """
    Return successfully indexed CAP domains as
    (domain_number, unit_cell) pairs.

    The order of the returned list follows the order
    of the parsed CAP domains.
    """

    parsed_result = results.get("parsed_result")

    if parsed_result is None:
        return []

    domains: list[tuple[int, UnitCell]] = []

    for domain in parsed_result.domains:
        if domain.unit_cell is not None:
            domains.append(
                (
                    domain.domain_number,
                    domain.unit_cell,
                )
            )

    return domains