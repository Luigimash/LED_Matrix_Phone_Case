from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
from PIL import Image

from .utils import ensure_directory, sanitize_base_name, to_uint8


class ExportError(Exception):
    """Raised when frames cannot be exported."""


SUPPORTED_FORMATS = {"png", "pgm"}


def _prepare_output_dirs(output_dir: str | Path, base_name: str) -> tuple[Path, Path]:
    root = ensure_directory(output_dir)
    base = sanitize_base_name(base_name)
    frame_dir = root / base
    ensure_directory(frame_dir)
    metadata_path = root / "metadata.json"
    return frame_dir, metadata_path


def export_frames(
    frames: Iterable[np.ndarray],
    output_dir: str | Path,
    base_name: str,
    *,
    fps: Optional[float] = None,
    source_path: str | Path | None = None,
    file_format: str = "png",
) -> dict:
    """Export processed frames to disk and write metadata."""
    normalized_format = file_format.lower()
    if normalized_format not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported output format '{file_format}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    frame_dir, metadata_path = _prepare_output_dirs(output_dir, base_name)

    frame_paths: list[Path] = []
    width = height = None
    extension = ".png" if normalized_format == "png" else ".pgm"

    for index, frame in enumerate(frames, start=1):
        array = np.asarray(frame)
        if array.ndim != 2:
            raise ExportError("Processed frames must be 2D grayscale arrays")

        array = to_uint8(array)
        if width is None or height is None:
            height, width = array.shape

        filename = f"frame_{index:04d}{extension}"
        path = frame_dir / filename
        if normalized_format == "png":
            Image.fromarray(array, mode="L").save(path, format="PNG")
        else:
            _write_ascii_pgm(path, array)
        frame_paths.append(path)

    if not frame_paths:
        raise ExportError("No frames were exported; ensure input media contains frames.")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source_path) if source_path else None,
        "base_name": sanitize_base_name(base_name),
        "frame_dir": str(frame_dir),
        "frame_count": len(frame_paths),
        "fps": fps,
        "dimensions": {"width": width, "height": height},
        "frame_format": normalized_format,
        "frames": [str(path.relative_to(frame_dir.parent)) for path in frame_paths],
    }

    _write_metadata(metadata_path, metadata)

    return {"frame_dir": str(frame_dir), "metadata_path": str(metadata_path), "metadata": metadata}


def _write_metadata(path: Path, metadata: dict) -> None:
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        existing = {}
    except json.JSONDecodeError:
        existing = {}

    base_name = metadata["base_name"]
    existing[base_name] = metadata

    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def _write_ascii_pgm(path: Path, array: np.ndarray) -> None:
    """Write a grayscale frame as an ASCII PGM file."""
    height, width = array.shape
    header = f"P2\n{width} {height}\n255\n"
    with path.open("w", encoding="utf-8") as handle:
        handle.write(header)
        for row in array:
            handle.write(" ".join(str(int(value)) for value in row))
            handle.write("\n")


