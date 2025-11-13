from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image

from . import export_frames, process_frames, stream_media
from .exporter import ExportError
from .loader import MediaLoadError
from .utils import sanitize_base_name


INTERPOLATION_OPTIONS = {
    "nearest": Image.NEAREST,
    "bilinear": Image.BILINEAR,
    "bicubic": Image.BICUBIC,
    "lanczos": Image.LANCZOS,
}

OUTPUT_FORMATS = ("png", "pgm")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert media files into 28x20 grayscale frames for the LED matrix."
    )
    parser.add_argument("input", help="Path to an image, GIF, or video file.")
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory for generated frames and metadata (default: ./output).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=20,
        help="Target width for the LED matrix (default: 20).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=28,
        help="Target height for the LED matrix (default: 28).",
    )
    parser.add_argument(
        "--interpolation",
        choices=INTERPOLATION_OPTIONS.keys(),
        default="lanczos",
        help="Resampling filter to use during resizing (default: lanczos).",
    )
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="png",
        help="Output frame format. Use 'pgm' for ASCII grayscale values (default: png).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing frame directory if it already exists.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser().resolve()

    try:
        frame_iterator, media_info = stream_media(input_path)
    except (MediaLoadError, FileNotFoundError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    base_name = sanitize_base_name(input_path.stem)
    output_root = Path(args.output).expanduser().resolve()
    frame_dir = output_root / base_name

    if frame_dir.exists():
        if args.overwrite:
            shutil.rmtree(frame_dir)
        else:
            print(
                f"[error] Output directory already exists: {frame_dir}. "
                "Use --overwrite to replace it.",
                file=sys.stderr,
            )
            return 1

    resample = INTERPOLATION_OPTIONS[args.interpolation]
    processed_frames = process_frames(
        frame_iterator,
        target_width=args.width,
        target_height=args.height,
        resample=resample,
    )

    try:
        result = export_frames(
            processed_frames,
            output_root,
            base_name,
            fps=media_info.fps,
            source_path=input_path,
            file_format=args.format,
        )
    except ExportError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    metadata = result["metadata"]
    print(f"[ok] Processed {metadata['frame_count']} frame(s) → {metadata['frame_dir']}")
    print(f"[ok] Metadata written to {result['metadata_path']}")
    if metadata["fps"]:
        print(f"[info] Source FPS: {metadata['fps']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


