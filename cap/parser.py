import re

from core.models import CAPDomain, CAPResult, UnitCell


# ------------------------------------------------------------
# Regular expressions
# ------------------------------------------------------------

UNIT_CELL_PATTERN = re.compile(
    r"""
    unit\ cell:\s*
    ([0-9.]+)\(\d+\)\s+
    ([0-9.]+)\(\d+\)\s+
    ([0-9.]+)\(\d+\)
    \s+
    ([0-9.]+)\(\d+\)\s+
    ([0-9.]+)\(\d+\)\s+
    ([0-9.]+)\(\d+\)
    """,
    re.IGNORECASE | re.VERBOSE,
)


INDEXING_PATTERN = re.compile(
    r"""
    UB\ fit\ with\s+
    (\d+)\s+obs\s+out\s+of\s+
    (\d+)
    .*?
    \(([\d.]+)%\)
    """,
    re.IGNORECASE | re.VERBOSE,
)


DOMAIN_PATTERN = re.compile(
    r"Searching cell for component #(\d+)",
    re.IGNORECASE,
)


ERROR_PATTERN = re.compile(
    r"(?:UM\s+\w+\s+)?ERROR:\s*(.+)",
    re.IGNORECASE,
)


WARNING_PATTERN = re.compile(
    r"(?:UM\s+\w+\s+)?WARNING:\s*(.+)",
    re.IGNORECASE,
)


# ------------------------------------------------------------
# Unit-cell parsing
# ------------------------------------------------------------

def _parse_unit_cell(match: re.Match) -> UnitCell:
    """
    Convert a CrysAlisPro unit-cell regex match
    into a UnitCell object.
    """

    values = [
        float(value)
        for value in match.groups()
    ]

    return UnitCell(
        a=values[0],
        b=values[1],
        c=values[2],
        alpha=values[3],
        beta=values[4],
        gamma=values[5],
        source="CAP",
    )


# ------------------------------------------------------------
# TWINTTT domain parsing
# ------------------------------------------------------------

def _parse_twinttt_domains(
    log_output: str,
) -> list[CAPDomain]:
    """
    Parse crystal domains from CrysAlisPro UM TWINTTT output.

    Each section beginning with:

        Searching cell for component #N...

    represents one possible crystal component.

    A component is only returned as a CAPDomain if
    CrysAlisPro successfully produced a unit cell for it.

    The final refined unconstrained unit cell is preferred.
    The final UB-fit indexing result is used.
    """

    domain_matches = list(
        DOMAIN_PATTERN.finditer(log_output)
    )

    domains: list[CAPDomain] = []

    for index, domain_match in enumerate(domain_matches):

        domain_number = int(
            domain_match.group(1)
        )

        # ----------------------------------------------------
        # Determine component section
        # ----------------------------------------------------

        start = domain_match.end()

        if index + 1 < len(domain_matches):
            end = domain_matches[index + 1].start()
        else:
            end = len(log_output)

        section = log_output[start:end]

        # ----------------------------------------------------
        # Ignore failed components
        # ----------------------------------------------------

        if re.search(
            r"Failed to find the cell",
            section,
            re.IGNORECASE,
        ):
            continue

        domain = CAPDomain(
            domain_number=domain_number
        )

        # ----------------------------------------------------
        # Unit cell
        # ----------------------------------------------------

        unit_cells = list(
            UNIT_CELL_PATTERN.finditer(section)
        )

        if unit_cells:

            # Prefer the refined unconstrained cell.
            #
            # CrysAlisPro normally contains:
            #
            #   No constraint
            #   ...
            #   unit cell: ...
            #
            # followed later by:
            #
            #   Constraint
            #   ...
            #   unit cell: ...
            #
            # The first unit-cell result after the final
            # "No constraint" marker is therefore preferred.

            no_constraint_positions = [
                match.start()
                for match in re.finditer(
                    r"\bNo constraint\b",
                    section,
                    re.IGNORECASE,
                )
            ]

            selected_cell = None

            if no_constraint_positions:

                position = no_constraint_positions[-1]

                for cell_match in unit_cells:

                    if cell_match.start() > position:
                        selected_cell = cell_match
                        break

            # Fallback if no "No constraint" block exists.
            if selected_cell is None:
                selected_cell = unit_cells[-1]

            domain.unit_cell = _parse_unit_cell(
                selected_cell
            )

        # ----------------------------------------------------
        # Indexing
        # ----------------------------------------------------

        indexing_matches = list(
            INDEXING_PATTERN.finditer(section)
        )

        if indexing_matches:

            # Use the final UB-fit result for this component.

            match = indexing_matches[-1]

            domain.indexed_reflections = int(
                match.group(1)
            )

            domain.total_reflections = int(
                match.group(2)
            )

            domain.indexing_percent = float(
                match.group(3)
            )

        # ----------------------------------------------------
        # Only retain a genuine domain
        # ----------------------------------------------------

        if domain.unit_cell is not None:
            domains.append(domain)

    return domains


# ------------------------------------------------------------
# TTT single-domain parsing
# ------------------------------------------------------------

def _parse_ttt_domain(
    log_output: str,
) -> list[CAPDomain]:
    """
    Parse a single crystal domain from CrysAlisPro UM TTT output.

    UM TTT does not contain the component sections used by
    UM TWINTTT. Instead, the output contains several candidate
    cells followed by UB-fit refinement.

    The final UB-fit result is used.

    For example:

        UB fit with 315 obs out of 370 ... (85.14%)
            unit cell:
              12.362(4) 19.618(8) 24.606(7)
              89.72(3)  89.63(3)  89.94(3)
              V = 5967(4)

            unit cell:
              12.3655(18) 19.615(4) 24.601(7)
              90.0 90.0 90.0

    The first unit cell after the final UB-fit line is used.
    This is the refined unconstrained cell rather than the
    subsequently constrained cell.
    """

    indexing_matches = list(
        INDEXING_PATTERN.finditer(log_output)
    )

    if not indexing_matches:
        return []

    # Use the final UB-fit result.
    indexing_match = indexing_matches[-1]

    indexed_reflections = int(
        indexing_match.group(1)
    )

    total_reflections = int(
        indexing_match.group(2)
    )

    indexing_percent = float(
        indexing_match.group(3)
    )

    # --------------------------------------------------------
    # Find the refined unit cell associated with that UB fit
    # --------------------------------------------------------

    unit_cell_matches = [
        match
        for match in UNIT_CELL_PATTERN.finditer(
            log_output
        )
        if match.start() > indexing_match.end()
    ]

    if not unit_cell_matches:
        return []

    # The first unit cell after the final UB-fit result is
    # the refined unconstrained cell. The second is normally
    # the constrained cell.
    selected_cell = unit_cell_matches[0]

    domain = CAPDomain(
        domain_number=1,
        unit_cell=_parse_unit_cell(
            selected_cell
        ),
        indexed_reflections=indexed_reflections,
        total_reflections=total_reflections,
        indexing_percent=indexing_percent,
    )

    return [domain]


# ------------------------------------------------------------
# Domain parsing
# ------------------------------------------------------------

def parse_cap_domains(
    log_output: str,
) -> list[CAPDomain]:
    """
    Parse CAP crystal domains.

    The parser automatically detects the CAP command format:

        UM TWINTTT
            -> one CAPDomain per component

        UM TTT
            -> one CAPDomain for the single indexed crystal

    This allows the same parser to be used regardless of
    whether the configured CAP command is "um ttt" or
    "um twinttt".
    """

    # UM TWINTTT contains explicit component sections.
    #
    # We use the presence of:
    #
    #     Searching cell for component #N
    #
    # as the format discriminator rather than relying only
    # on the command text. This is more robust if CAP wraps
    # or changes the command header.

    if DOMAIN_PATTERN.search(log_output):
        return _parse_twinttt_domains(
            log_output
        )

    # UM TTT has no component sections and therefore falls
    # through to the single-domain parser.
    return _parse_ttt_domain(
        log_output
    )


# ------------------------------------------------------------
# Error parsing
# ------------------------------------------------------------

def parse_cap_errors(
    log_output: str,
) -> list[str]:
    """
    Extract CrysAlisPro errors from CAP log output.
    """

    return [
        match.group(1).strip()
        for match in ERROR_PATTERN.finditer(
            log_output
        )
    ]


# ------------------------------------------------------------
# Warning parsing
# ------------------------------------------------------------

def parse_cap_warnings(
    log_output: str,
) -> list[str]:
    """
    Extract CrysAlisPro warnings from CAP log output.
    """

    return [
        match.group(1).strip()
        for match in WARNING_PATTERN.finditer(
            log_output
        )
    ]


# ------------------------------------------------------------
# Complete CAP result
# ------------------------------------------------------------

def parse_cap_result(
    log_output: str,
    success: bool,
) -> CAPResult:
    """
    Parse a complete CrysAlisPro indexing result.

    Automatically supports both:

        UM TTT
        UM TWINTTT

    Returns:

        CAPResult
            success
            domains
            errors
            warnings
    """

    errors = parse_cap_errors(
        log_output
    )

    warnings = parse_cap_warnings(
        log_output
    )

    domains = parse_cap_domains(
        log_output
    )

    return CAPResult(
        success=success,
        domains=domains,
        errors=errors,
        warnings=warnings,
    )


# ------------------------------------------------------------
# Compatibility aliases
# ------------------------------------------------------------

# Keep compatibility with existing cap/indexing.py and any
# older code that may import one of these parser names.

parse_cap_unit_cell_result = parse_cap_result
parse_result = parse_cap_result
