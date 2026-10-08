from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from core.models import Dataset


def _format_cell(cell) -> str:
    """Format a UnitCell for display in the HTML table."""

    if cell is None:
        return "—"

    return (
        f"{cell.a:.4f}, "
        f"{cell.b:.4f}, "
        f"{cell.c:.4f}, "
        f"{cell.alpha:.3f}, "
        f"{cell.beta:.3f}, "
        f"{cell.gamma:.3f}"
    )


def _format_indexing(value: float | None) -> str:
    """Format CAP indexing percentage."""

    if value is None:
        return "—"

    return f"{value:.2f}%"


def _dataset_rows(dataset: Dataset) -> list[str]:
    """
    Create HTML table rows for one Dataset.

    One row is created for each successful CAP domain.
    If no CAP domain exists, one row is still created so
    that the dataset remains visible in the report.
    """

    metadata = [
        dataset.name,
        (
            dataset.modification_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if dataset.modification_date is not None
            else "—"
        ),
        (
            f"{dataset.folder_size_mb:.2f}"
            if dataset.folder_size_mb is not None
            else "—"
        ),
    ]

    ins_cell = _format_cell(
        dataset.unit_cell
    )

    domains = []

    if dataset.cap_result is not None:
        domains = dataset.cap_result.domains

    if not domains:
        domains = [None]

    rows = []

    for domain in domains:

        if domain is None:
            domain_number = "—"
            cap_cell = "—"
            indexing = "—"
            gemmi_cell = "—"
            cluster = "—"
            row_class = "no-cap"

        else:
            domain_number = str(
                domain.domain_number
            )
            cap_cell = _format_cell(
                domain.unit_cell
            )
            indexing = _format_indexing(
                domain.indexing_percent
            )
            gemmi_cell = _format_cell(
                domain.reduced_unit_cell
            )
            cluster = (
                domain.cluster
                if domain.cluster is not None
                else "—"
            )

            row_class = (
                "success"
                if domain.unit_cell is not None
                else "failed"
            )

        cells = [
            *metadata,
            ins_cell,
            domain_number,
            cap_cell,
            indexing,
            gemmi_cell,
            cluster,
        ]

        row = (
            f'<tr class="{row_class}">'
            + "".join(
                f"<td>{escape(str(value))}</td>"
                for value in cells
            )
            + "</tr>"
        )

        rows.append(row)

    return rows


def write_html_report(
    datasets: list[Dataset],
    output_file: Path | str,
    total_datasets: int | None = None,
    auto_refresh_seconds: int = 5,
    processing_complete: bool = False,
) -> Path:
    """
    Write or overwrite the live HTML processing report.

    The same file can be rewritten after every processed
    dataset. A browser can automatically refresh the page.
    """

    output_file = Path(output_file)
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if total_datasets is None:
        total_datasets = len(datasets)

    rows = []

    for dataset in datasets:
        rows.extend(
            _dataset_rows(dataset)
        )

    completed = len(datasets)

    if processing_complete:
        status = (
            f"Processing complete — "
            f"{completed}/{total_datasets} datasets"
        )
    else:
        status = (
            f"Processing — "
            f"{completed}/{total_datasets} datasets"
        )

    refresh_tag = ""

    if not processing_complete:
        refresh_tag = (
            f'<meta http-equiv="refresh" '
            f'content="{auto_refresh_seconds}">'
        )

    generated_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    table_body = (
        "\n".join(rows)
        if rows
        else (
            '<tr class="empty">'
            '<td colspan="9">'
            'No datasets processed yet.'
            '</td>'
            '</tr>'
        )
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{refresh_tag}
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>RA3 Crystallographic Processing</title>

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 24px;
    background: #f5f5f5;
    color: #222;
}}

h1 {{
    margin-bottom: 8px;
}}

.status {{
    margin-bottom: 20px;
    padding: 12px 16px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    font-size: 13px;
}}

th {{
    background: #333;
    color: white;
    padding: 9px;
    text-align: left;
    position: sticky;
    top: 0;
}}

td {{
    padding: 8px;
    border-bottom: 1px solid #ddd;
    white-space: nowrap;
}}

tr.success {{
    background: #f0fff0;
}}

tr.failed {{
    background: #fff0f0;
}}

tr.no-cap {{
    background: #fffdf0;
}}

tr.empty {{
    text-align: center;
}}

.legend {{
    margin-top: 15px;
    font-size: 13px;
}}

.small {{
    color: #666;
    font-size: 12px;
}}
</style>
</head>

<body>

<h1>RA3 Crystallographic Processing</h1>

<div class="status">
    <strong>{escape(status)}</strong>
    <br>
    <span class="small">
        Last updated: {escape(generated_time)}
    </span>
</div>

<table>
<thead>
<tr>
    <th>Dataset</th>
    <th>Modification Date</th>
    <th>Folder Size (MB)</th>
    <th>INS-UC<br>a,b,c,α,β,γ</th>
    <th>CAP Domain</th>
    <th>CAP-UC<br>a,b,c,α,β,γ</th>
    <th>Indexing</th>
    <th>Gemmi-UC<br>a,b,c,α,β,γ</th>
    <th>Cluster</th>
</tr>
</thead>

<tbody>
{table_body}
</tbody>
</table>

<div class="legend">
    <strong>Row status:</strong>
    successful CAP domain = light green;
    failed/no CAP result = light red/yellow.
</div>

</body>
</html>
"""

    output_file.write_text(
        html,
        encoding="utf-8",
    )

    return output_file


__all__ = [
    "write_html_report",
]
