from __future__ import annotations

from config import PHASE_COLOURS


def get_phase_colour(
    phase_number: int,
) -> str:
    """
    Return the Excel fill colour for a phase number.

    Colours are cycled if the number of phases exceeds the
    configured colour list.
    """

    if phase_number < 1:
        raise ValueError(
            "Phase number must be >= 1."
        )

    if not PHASE_COLOURS:
        raise ValueError(
            "PHASE_COLOURS is empty."
        )

    index = (phase_number - 1) % len(
        PHASE_COLOURS
    )

    return PHASE_COLOURS[index]


def get_cluster_colour(
    cluster_name: str | None,
) -> str | None:
    """
    Return the Excel colour associated with a cluster name.

    Expected cluster names:

        RA3-1
        RA3-2
        RA3-3
        ...

    Returns None when the cluster name cannot be interpreted.
    """

    if not cluster_name:
        return None

    try:
        phase_number = int(
            cluster_name.rsplit("-", 1)[1]
        )

    except (IndexError, ValueError):
        return None

    return get_phase_colour(
        phase_number
    )