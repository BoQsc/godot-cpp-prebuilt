#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    p.add_argument("--api-version", required=True)
    p.add_argument("--godot-cpp-sha", required=True)
    p.add_argument("--output", default="manifest.json")
    args = p.parse_args()

    directory = Path(args.directory)
    assets = []

    for path in sorted(directory.glob("*.zip")):
        assets.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest = {
        "api_version": args.api_version,
        "godot_cpp_sha": args.godot_cpp_sha,
        "assets": assets,
    }

    output = Path(args.output)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
