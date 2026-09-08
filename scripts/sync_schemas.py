"""Copy packaged schema resources to the root public schema directory."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "cutoffguard" / "schemas"
TARGET = ROOT / "schemas"


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob("*.json")):
        shutil.copyfile(source, TARGET / source.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
