#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "builds.json").read_text(encoding="utf-8"))

REQUIRED_VARIANTS = {
    "linux-x86_64-gcc",
    "windows-x86_64-msvc",
    "windows-x86_64-mingw",
    "macos-universal-clang",
    "android-arm64",
    "ios-arm64",
    "web-wasm32",
}


def main() -> int:
    api = CONFIG.get("default_api_version")
    ref = CONFIG.get("godot_cpp", {}).get("ref")
    variants = CONFIG.get("variants", [])
    errors = []

    if not isinstance(api, str) or not api:
        errors.append("default_api_version is missing.")
    if not isinstance(ref, str) or len(ref) < 7:
        errors.append("godot_cpp.ref is missing or too short.")

    ids = [item.get("id") for item in variants]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate variant IDs.")

    missing = sorted(REQUIRED_VARIANTS - set(ids))
    unexpected = sorted(set(ids) - REQUIRED_VARIANTS)
    if missing:
        errors.append("Missing variants: " + ", ".join(missing))
    if unexpected:
        errors.append("Unexpected variants: " + ", ".join(unexpected))

    for variant in variants:
        for key in ("id", "os", "platform", "arch", "compiler", "flags"):
            if key not in variant:
                errors.append(f"{variant.get('id', '<unknown>')}: missing {key}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    print("Configuration OK")
    print("API:", api)
    print("godot-cpp ref:", ref)
    print("variants:", len(variants))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
