#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
import zipfile


EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".scons_cache",
    "__pycache__",
    "test",
}
EXCLUDE_SUFFIXES = {
    ".o",
    ".obj",
    ".os",
    ".pyc",
}


def ignore_path(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    if path.name in {".sconsign.dblite", "compile_commands.json"}:
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return False


def copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if ignore_path(relative):
            continue

        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--api-version", required=True)
    parser.add_argument("--godot-cpp-sha", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--precision", required=True, choices=("single", "double"))
    parser.add_argument("--zig-version", default="")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="godot-cpp-package-") as td:
        package_root = Path(td) / "godot-cpp"
        package_root.mkdir(parents=True)

        copy_tree(source, package_root)

        info = {
            "api_version": args.api_version,
            "godot_cpp_sha": args.godot_cpp_sha,
            "variant": args.variant,
            "compiler": args.compiler,
            "platform": args.platform,
            "arch": args.arch,
            "zig_version": args.zig_version or None,
            "targets": ["template_debug", "template_release"],
            "precision": args.precision,
            "created_unix": int(time.time()),
        }
        (package_root / "BUILD_INFO.json").write_text(
            json.dumps(info, indent=2) + "\n",
            encoding="utf-8",
        )

        (package_root / "PREBUILT.md").write_text(
            """# Prebuilt package

This directory contains precompiled godot-cpp libraries.

Use the normal upstream SConstruct, but disable rebuilding the static library:

    scons build_library=no api_version=YOUR_API_VERSION

The generated bindings and prebuilt libraries are already present.
""",
            encoding="utf-8",
        )

        with zipfile.ZipFile(
            output,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path in sorted(package_root.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(package_root.parent))

    print(output)
    print("sha256:", sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
