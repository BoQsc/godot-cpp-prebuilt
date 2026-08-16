#!/usr/bin/env python3

"""Explicit Windows/MSVC recovery build.

Normal use should be GitHub Actions + release downloads.
A double-precision recovery build requires a genuine API dump from a
precision=double Godot editor, supplied with GODOT_CPP_DOUBLE_API.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "builds.json").read_text(encoding="utf-8"))
API = CONFIG["default_api_version"]
REF = CONFIG["godot_cpp"]["ref"]


def download(url: str, output: Path) -> None:
    print("Downloading:", url)
    request = urllib.request.Request(url, headers={"User-Agent": "godot-cpp-prebuilt-local-build"})
    with urllib.request.urlopen(request) as response, output.open("wb") as f:
        shutil.copyfileobj(response, f)


def ensure_scons() -> None:
    if importlib.util.find_spec("SCons") is None:
        print("Installing SCons...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scons==4.4.0"])


def ensure_upstream() -> Path:
    target = ROOT / "godot-cpp"
    if (target / "SConstruct").is_file():
        return target

    url = f"https://github.com/godotengine/godot-cpp/archive/{REF}.zip"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        archive = td / "godot-cpp.zip"
        extract = td / "extract"
        download(url, archive)
        with zipfile.ZipFile(archive) as z:
            z.extractall(extract)
        source = next(p for p in extract.iterdir() if p.is_dir())
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(source), str(target))
    return target


def bundled_api_path(upstream: Path) -> Path:
    return upstream / "gdextension" / f"extension_api-{API.replace('.', '-')}.json"


def validate_api(path: Path, precision: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    actual = data.get("header", {}).get("precision")
    if actual != precision:
        raise RuntimeError(f"{path} has precision={actual!r}; expected {precision!r}")


def run_build(target: str, precision: str) -> None:
    cmd = [
        sys.executable,
        "-m",
        "SCons",
        f"api_version={API}",
        "platform=windows",
        "arch=x86_64",
        f"target={target}",
        f"precision={precision}",
        "-j4",
    ]
    print(" ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT / "godot-cpp")


def package_precision(precision: str) -> None:
    output = ROOT / f"godot-cpp-api-{API}-windows-x86_64-msvc-{precision}.zip"
    subprocess.check_call([
        sys.executable,
        "scripts/package.py",
        "--source", "godot-cpp",
        "--output", str(output),
        "--api-version", API,
        "--godot-cpp-sha", REF,
        "--variant", "windows-x86_64-msvc",
        "--compiler", "msvc",
        "--platform", "windows",
        "--arch", "x86_64",
        "--precision", precision,
    ], cwd=ROOT)
    print("Created:", output)


def main() -> int:
    if sys.platform != "win32":
        print("ERROR: this recovery helper is intentionally Windows/MSVC only.")
        return 2

    ensure_scons()
    upstream = ensure_upstream()
    api_path = bundled_api_path(upstream)
    original_api = api_path.read_bytes()

    try:
        validate_api(api_path, "single")
        for target in ("template_debug", "template_release"):
            run_build(target, "single")
        package_precision("single")

        double_api_raw = os.environ.get("GODOT_CPP_DOUBLE_API", "").strip()
        if not double_api_raw:
            print("Skipping double-precision recovery build.")
            print("Set GODOT_CPP_DOUBLE_API to a genuine extension_api.json dumped by a precision=double Godot editor.")
            return 0

        double_api = Path(double_api_raw).expanduser().resolve()
        if not double_api.is_file():
            raise RuntimeError(f"GODOT_CPP_DOUBLE_API does not exist: {double_api}")
        validate_api(double_api, "double")
        shutil.copy2(double_api, api_path)

        for target in ("template_debug", "template_release"):
            run_build(target, "double")
        package_precision("double")
    finally:
        api_path.write_bytes(original_api)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
