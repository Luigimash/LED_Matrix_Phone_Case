from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import imageio.v2 as imageio
import numpy as np

from .utils import resolve_path, to_uint8


class MediaLoadError(Exception):
    """Raised when a media file cannot be loaded."""


@dataclass(slots=True)
class MediaInfo:
    path: Path
    format: Optional[str] = None
    fps: Optional[float] = None
    duration: Optional[float] = None
    frame_count: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


def stream_media(filepath: str | Path) -> tuple[Iterator[np.ndarray], MediaInfo]:
    """Load a media file and stream its frames as numpy arrays."""
    resolved = resolve_path(filepath)
    if resolved.is_dir():
        raise MediaLoadError(f"Expected file but got directory: {resolved}")

    try:
        reader = imageio.get_reader(resolved.as_posix())
    except Exception as exc:  # pragma: no cover - logging not yet implemented
        raise MediaLoadError(f"Failed to open media file: {resolved}") from exc

    info = MediaInfo(path=resolved)

    try:
        meta = reader.get_meta_data()
    except Exception:  # pragma: no cover - imageio may raise on some formats
        meta = {}

    info.format = meta.get("format") or meta.get("codec") or resolved.suffix.lstrip(".")
    info.fps = meta.get("fps")
    info.duration = meta.get("duration")
    info.frame_count = meta.get("nframes") or meta.get("n_frames")

    def frame_generator() -> Iterator[np.ndarray]:
        nonlocal reader
        try:
            for frame in reader:
                array = to_uint8(np.asarray(frame))
                if info.width is None or info.height is None:
                    info.height, info.width = array.shape[:2]
                yield array
        finally:
            reader.close()

    # Verify the reader can provide at least one frame. If not, fall back.
    iterator = frame_generator()
    try:
        first_frame = next(iterator)
    except StopIteration:
        reader.close()
        try:
            single_frame = imageio.imread(resolved.as_posix())
        except Exception as img_exc:
            raise MediaLoadError(f"Unable to read media: {resolved}") from img_exc

        array = to_uint8(np.asarray(single_frame))
        info.height, info.width = array.shape[:2]
        info.frame_count = 1

        def single_frame_gen() -> Iterator[np.ndarray]:
            yield array

        return single_frame_gen(), info

    def chain_generator() -> Iterator[np.ndarray]:
        yield first_frame
        for frame in iterator:
            yield frame

    if info.frame_count is None:
        info.frame_count = None  # explicit for clarity

    return chain_generator(), info


def load_media(filepath: str | Path) -> list[np.ndarray]:
    """Load all frames into memory as a list (may be expensive for large videos)."""
    frames, _ = stream_media(filepath)
    return list(frames)


