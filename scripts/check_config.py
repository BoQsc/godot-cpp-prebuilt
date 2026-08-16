#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "builds.json").read_text(encoding="utf-8"))

REQUIRED_VARIANTS = {
    "linux-x86_64-gcc", "windows-x86_64-msvc", "windows-x86_64-mingw",
    "windows-x86_64-zig", "macos-universal-clang", "android-arm64",
    "ios-arm64", "web-wasm32",
}


def main() -> int:
    api = CONFIG.get("default_api_version")
    ref = CONFIG.get("godot_cpp", {}).get("ref")
    zig = CONFIG.get("zig", {})
    variants = CONFIG.get("variants", [])
    errors = []

    if not isinstance(api, str) or not api:
        errors.append("default_api_version is missing.")
    if not isinstance(ref, str) or len(ref) < 7:
        errors.append("godot_cpp.ref is missing or too short.")

    zig_version = zig.get("version")
    zig_url = zig.get("windows_x86_64_url")
    zig_sha = zig.get("windows_x86_64_sha256")
    if not isinstance(zig_version, str) or not zig_version:
        errors.append("zig.version is missing.")
    if not isinstance(zig_url, str) or urlparse(zig_url).scheme != "https":
        errors.append("zig.windows_x86_64_url must be an HTTPS URL.")
    elif isinstance(zig_version, str) and zig_version not in zig_url:
        errors.append("zig.windows_x86_64_url does not contain zig.version.")
    if not isinstance(zig_sha, str) or len(zig_sha) != 64:
        errors.append("zig.windows_x86_64_sha256 must be a 64-character SHA256 digest.")

    ids = [item.get("id") for item in variants]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate variant IDs.")
    missing = sorted(REQUIRED_VARIANTS - set(ids))
    if missing:
        errors.append("Missing variants: " + ", ".join(missing))

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
    print("Zig:", zig_version)
    print("variants:", len(variants))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
