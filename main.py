#!/usr/bin/env python3
"""news-image-20261122 entry: Sunday 22 November 2026 in one image.

The front-page image (entry.png, 1024x1024) was rendered at build time
with real TrueType fonts and flat vector-style illustrations. This
program runs on the grader with the Python standard library only: it
validates the bundled PNG and copies it, byte for byte, to the output
directory as entry.png. Both grader runs therefore write identical
bytes, with no network and no third-party imports.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def output_dir() -> Path:
    """Grader output folder: env override first, then /output."""
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return Path(env)
    default = Path("/output")
    if default.is_dir():
        return default
    return Path("output")


def png_size(data: bytes) -> tuple[int, int]:
    """Read width/height from the IHDR chunk without any image library."""
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
        raise ValueError("bundled file is not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def find_source() -> Path:
    """Bundled image: next to this script, else the working directory."""
    here = Path(__file__).resolve().parent
    for candidate in (here / "entry.png", Path.cwd() / "entry.png"):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("entry.png not found beside main.py or in the working directory")


def main() -> int:
    source = find_source()
    data = source.read_bytes()

    if len(data) > MAX_BYTES:
        print(f"entry.png is {len(data)} bytes, over the 1 MiB limit", file=sys.stderr)
        return 1
    width, height = png_size(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        print(f"entry.png is {width}x{height}, over the 1024 limit", file=sys.stderr)
        return 1

    target_dir = output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "entry.png"
    # Write via a temp file in the same folder, then rename, so a
    # half-written entry.png can never be left behind.
    tmp = target_dir / ".entry.png.tmp"
    tmp.write_bytes(data)
    tmp.replace(target)

    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {target} ({width}x{height}, {len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
