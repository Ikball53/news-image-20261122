"""News image entry for Sunday 22 November 2026.

Copies the bundled front-page image beside this file to the
grader output path, byte for byte, on every run.
"""

from pathlib import Path
import shutil


def main() -> None:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        raise FileNotFoundError(f"missing bundled image: {source}")
    target = Path("/output/entry.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert target.stat().st_size == source.stat().st_size


if __name__ == "__main__":
    main()
