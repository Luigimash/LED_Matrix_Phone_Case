from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np


def resolve_path(path: str | Path) -> Path:
    """Resolve a filesystem path and ensure it exists."""
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")
    return resolved


def ensure_directory(path: str | Path) -> Path:
    """Create a directory (and parents) if it does not exist."""
    directory = Path(path).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def sanitize_base_name(name: str) -> str:
    """Generate a filesystem-friendly base name."""
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return sanitized or "output"


def to_uint8(array: np.ndarray) -> np.ndarray:
    """Convert an arbitrary numeric array to uint8 in the 0-255 range."""
    if array.dtype == np.uint8:
        return array

    if np.issubdtype(array.dtype, np.floating):
        max_value = array.max(initial=0)
        data = array.copy()
        if max_value <= 1.0:
            data *= 255.0
    else:
        data = array.astype(np.float32, copy=False)

    data = np.clip(data, 0, 255)
    return data.astype(np.uint8)


def first(iterable: Iterable) -> object | None:
    """Return the first item in an iterable without consuming more than needed."""
    for item in iterable:
        return item
    return None


