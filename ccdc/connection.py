"""Optional CCDC availability check."""


def is_available() -> bool:
    try:
        import ccdc  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        return False
    return True
