from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config import (
    EXCEL_CELL_FORMAT,
    EXCEL_DATE_FORMAT,
    EXCEL_FREEZE_PANES,
    EXCEL_SHEET_NAME,
    EXCEL_SIZE_FORMAT,
    OUTPUT_DIR,
    OUTPUT_PREFIX,
    ADD_TIMESTAMP_TO_FILENAME,
    TIMESTAMP_FORMAT,
    SIZE_UNIT,
)
from core.models import Dataset


def _output_filename() -> Path:
    """Create the configured Excel output filename."""
    filename = OUTPUT_PREFIX

    if ADD_TIMESTAMP_TO_FILENAME:
        filename += "_" + datetime.now().strftime(TIMESTAMP_FORMAT)

    return OUTPUT_DIR / f"{filename}.xlsx"


def _cell_values(cell) -> list[float | None]:
    """Return the six unit-cell parameters."""
    if cell is None:
        return [None] * 6

    return [
        cell.a,
        cell.b,
        cell.c,
        cell.alpha,
        cell.beta,
        cell.gamma,
    ]


def _dataset_rows(dataset: Dataset) -> list[list]:
    """
    Create Excel rows for one dataset.

    One row is created for each CAP domain. If no CAP domain
    exists, one row is still created so the dataset remains visible.
    """
    ins = _cell_values(dataset.unit_cell)

    domains = []
    if dataset.cap_result is not None:
        domains = dataset.cap_result.domains

    if not domains:
        domains = [None]

    rows = []

    for domain in domains:
        if domain is None:
            cap = [None] * 6
            domain_number = None
            indexed = None
            total = None
            indexing_percent = None
            gemmi = [None] * 6
            cluster = None
        else:
            cap = _cell_values(domain.unit_cell)
            domain_number = domain.domain_number
            indexed = domain.indexed_reflections
            total = domain.total_reflections
            indexing_percent = domain.indexing_percent
            gemmi = _cell_values(domain.reduced_unit_cell)
            cluster = domain.cluster

        rows.append(
            [
                dataset.name,
                dataset.modification_date,
                dataset.folder_size_mb,
                *ins,
                domain_number,
                *cap,
                indexed,
                total,
                indexing_percent,
                *gemmi,
                cluster,
            ]
        )

    return rows


def write_excel_report(
    datasets: list[Dataset],
    output_file: Path | str | None = None,
) -> Path:
    """
    Write the final crystallographic processing report to Excel.

    The workbook contains one Summary sheet with one row per CAP
    domain. Dataset metadata and the INS unit cell are repeated for
    each domain belonging to that dataset.
    """
    if output_file is None:
        output_file = _output_filename()
    else:
        output_file = Path(output_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = EXCEL_SHEET_NAME

    headers = [
        "Dataset",
        "Modification Date",
        f"Folder Size ({SIZE_UNIT})",

        "INS a (Å)",
        "INS b (Å)",
        "INS c (Å)",
        "INS α (°)",
        "INS β (°)",
        "INS γ (°)",

        "CAP Domain",

        "CAP a (Å)",
        "CAP b (Å)",
        "CAP c (Å)",
        "CAP α (°)",
        "CAP β (°)",
        "CAP γ (°)",

        "Indexed Reflections",
        "Total Reflections",
        "Indexing (%)",

        "Gemmi a (Å)",
        "Gemmi b (Å)",
        "Gemmi c (Å)",
        "Gemmi α (°)",
        "Gemmi β (°)",
        "Gemmi γ (°)",

        "Cluster",
    ]

    worksheet.append(headers)

    # Header formatting
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    # Data
    for dataset in datasets:
        for row in _dataset_rows(dataset):
            worksheet.append(row)

    # Date
    for cell in worksheet["B"][1:]:
        if cell.value is not None:
            cell.number_format = EXCEL_DATE_FORMAT

    # Folder size
    for cell in worksheet["C"][1:]:
        if cell.value is not None:
            cell.number_format = EXCEL_SIZE_FORMAT

    # Unit-cell numeric columns:
    # D:I   = INS
    # K:P   = CAP
    # T:Y   = Gemmi
    for column in (
        list(range(4, 10))
        + list(range(11, 17))
        + list(range(20, 26))
    ):
        letter = get_column_letter(column)

        for cell in worksheet[letter][1:]:
            if cell.value is not None:
                cell.number_format = EXCEL_CELL_FORMAT

    # Indexing percentage
    # Store the value as a true percentage so Excel can filter,
    # calculate and chart it correctly.
    for cell in worksheet["S"][1:]:
        if cell.value is not None:
            cell.value = cell.value / 100.0
            cell.number_format = "0.00%"

    # Alignment
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="center"
            )

    # Freeze header
    worksheet.freeze_panes = EXCEL_FREEZE_PANES

    # Autofilter
    worksheet.auto_filter.ref = worksheet.dimensions

    # Column widths
    widths = {
        "A": 24,
        "B": 22,
        "C": 18,

        "D": 13,
        "E": 13,
        "F": 13,
        "G": 13,
        "H": 13,
        "I": 13,

        "J": 13,

        "K": 13,
        "L": 13,
        "M": 13,
        "N": 13,
        "O": 13,
        "P": 13,

        "Q": 19,
        "R": 18,
        "S": 15,

        "T": 14,
        "U": 14,
        "V": 14,
        "W": 14,
        "X": 14,
        "Y": 14,

        "Z": 14,
    }

    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    # Add an Excel table-like header filter and alternating row shading
    # without imposing phase/cluster colours.
    header_fill = PatternFill(
        fill_type="solid",
        fgColor="D9E1F2",
    )

    for cell in worksheet[1]:
        cell.fill = header_fill

    # Optional cluster highlighting: same cluster gets the same fill.
    # The colours cycle through the configured PHASE_COLOURS list.
    try:
        from config import PHASE_COLOURS

        cluster_fills = {}

        for row in range(2, worksheet.max_row + 1):
            cluster = worksheet.cell(row=row, column=26).value

            if cluster is None:
                continue

            if cluster not in cluster_fills:
                colour = PHASE_COLOURS[
                    len(cluster_fills) % len(PHASE_COLOURS)
                ]
                cluster_fills[cluster] = PatternFill(
                    fill_type="solid",
                    fgColor=colour,
                )

            worksheet.cell(
                row=row,
                column=26,
            ).fill = cluster_fills[cluster]

    except ImportError:
        pass

    workbook.save(output_file)

    return output_file


__all__ = [
    "write_excel_report",
]
