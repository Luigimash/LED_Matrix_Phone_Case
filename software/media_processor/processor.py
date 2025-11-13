from __future__ import annotations

from typing import Iterable, Iterator

import numpy as np
from PIL import Image

from .utils import to_uint8


def _to_pil_image(frame: np.ndarray) -> Image.Image:
    array = to_uint8(np.asarray(frame))

    if array.ndim == 2:
        return Image.fromarray(array, mode="L")

    if array.ndim == 3:
        channels = array.shape[2]
        if channels == 3:
            return Image.fromarray(array, mode="RGB")
        if channels == 4:
            return Image.fromarray(array, mode="RGBA")

    raise ValueError(f"Unsupported frame shape: {array.shape}")


def process_frame(
    frame: np.ndarray,
    target_width: int = 20,
    target_height: int = 28,
    resample: int = Image.LANCZOS,
) -> np.ndarray:
    """Convert a frame to a grayscale 8-bit bitmap with the desired dimensions."""
    pil_image = _to_pil_image(frame)
    resized = pil_image.resize((target_width, target_height), resample=resample)
    grayscale = resized.convert("L")
    return np.asarray(grayscale, dtype=np.uint8)


def process_frames(
    frames: Iterable[np.ndarray],
    target_width: int = 20,
    target_height: int = 28,
    resample: int = Image.LANCZOS,
) -> Iterator[np.ndarray]:
    """Yield processed frames for an iterable of input frames."""
    for frame in frames:
        yield process_frame(
            frame,
            target_width=target_width,
            target_height=target_height,
            resample=resample,
        )


