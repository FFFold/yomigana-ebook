"""UniDic dictionary discovery helpers for the desktop GUI.

The full UniDic dictionary is large, so the packaged app should be allowed to
keep it outside the executable. ``YOMIGANA_UNIDIC_DIR`` is honoured by
``yomigana_ebook.yomituki``; this module resolves a usable dictionary path and
sets that environment variable before the worker imports the conversion code.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

DICDIR_ENV_VAR = "YOMIGANA_UNIDIC_DIR"
LEGACY_DICDIR_ENV_VAR = "YOMIGANA_UNICID_DIR"

# Files that indicate a real installed UniDic dictionary directory.
_PRIMARY_DIC_MARKERS = ("sys.dic", "lex.csv")
_SECONDARY_DIC_MARKERS = ("dicrc", "mecabrc")


def is_valid_unidic_dir(path: Path | str | None) -> bool:
    if not path:
        return False
    dicdir = Path(path)
    if not dicdir.is_dir():
        return False
    has_primary = any((dicdir / marker).is_file() for marker in _PRIMARY_DIC_MARKERS)
    has_secondary = any(
        (dicdir / marker).is_file() for marker in _SECONDARY_DIC_MARKERS
    )
    return has_primary and has_secondary


def _frozen_candidates() -> list[Path]:
    if not getattr(sys, "frozen", False):
        return []

    exe_dir = Path(sys.executable).resolve().parent
    return [
        # Onefile build with the dictionary next to the executable.
        exe_dir / "unidic" / "dicdir",
        # Onedir build with the dictionary bundled into PyInstaller's _internal.
        exe_dir / "_internal" / "unidic" / "dicdir",
    ]


def find_unidic_dir() -> Path | None:
    """Return a valid UniDic dictionary directory, or None."""
    env_dicdir = os.environ.get(DICDIR_ENV_VAR) or os.environ.get(LEGACY_DICDIR_ENV_VAR)
    candidates: list[Path | str | None] = [
        env_dicdir.strip() if env_dicdir else None,
    ]

    try:
        import unidic

        candidates.append(unidic.DICDIR)
    except Exception:
        pass

    candidates.extend(_frozen_candidates())

    for candidate in candidates:
        if is_valid_unidic_dir(candidate):
            return Path(candidate).resolve()

    return None


def configure_unidic_dir() -> Path | None:
    """Find a dictionary and export it via ``YOMIGANA_UNIDIC_DIR``.

    Returns the resolved dictionary path, or None when no valid dictionary is
    available. The environment variable is only set when a valid path exists.
    """
    dicdir = find_unidic_dir()
    if dicdir is None:
        return None

    os.environ[DICDIR_ENV_VAR] = str(dicdir)
    return dicdir
