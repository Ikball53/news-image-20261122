"""Emit the prepared poster for the 22 November 2026 news digest."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def resolve_output_dir() -> Path:
    configured = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path("/output")


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"


def load_poster_bytes(here: Path) -> bytes:
    poster = here / "entry.png"
    if not poster.is_file():
        raise FileNotFoundError(f"missing poster file: {poster}")
    payload = poster.read_bytes()
    if not payload:
        raise ValueError("poster file is empty")
    if not (payload.startswith(PNG_SIGNATURE) or payload.startswith(JPEG_SIGNATURE)):
        raise ValueError("poster bytes are neither PNG nor JPEG")
    if len(payload) > 1024 * 1024:
        raise ValueError("poster exceeds the 1 MiB limit")
    return payload


def write_poster(payload: bytes, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(payload)
    return target


def main() -> int:
    here = Path(__file__).resolve().parent
    try:
        data = load_poster_bytes(here)
        destination = write_poster(data, resolve_output_dir())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {len(data)} bytes to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
