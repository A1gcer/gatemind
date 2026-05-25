#!/usr/bin/env python3
from pathlib import Path
import shutil

OLD = Path("skills/self-evolution-engine")
NEW = Path("skills/gatemind/gates/legacy")


def main():
    NEW.mkdir(parents=True, exist_ok=True)
    src = OLD / "gates"
    if not src.exists():
        print("no old gates found")
        return
    for f in src.glob("check_*.sh"):
        dst = NEW / f.name
        shutil.copy2(f, dst)
        print(f"migrated: {f} -> {dst}")
    print("done")


if __name__ == "__main__":
    main()
