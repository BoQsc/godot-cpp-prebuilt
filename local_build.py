#!/usr/bin/env python3

"""
Explicit Windows/Zig recovery build.

Normal use should be GitHub Actions + release downloads.
"""

from __future__ import annotations

import importlib.util
import json
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
ZIG_URL = CONFIG["zig"]["windows_x86_64_url"]
ZIG_VERSION = CONFIG["zig"]["version"]


def download(url: str, output: Path):
    print("Downloading:", url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "godot-cpp-prebuilt-local-build"},
    )
    with urllib.request.urlopen(request) as response, output.open("wb") as f:
        shutil.copyfileobj(response, f)


def ensure_scons():
    if importlib.util.find_spec("SCons") is None:
        print("Installing SCons...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scons"])


def ensure_upstream():
    target = ROOT / "godot-cpp"
    if (target / "SConstruct").is_file():
        return

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


def ensure_zig():
    target = ROOT / "tools" / "zig"
    exe = target / "zig.exe"
    if exe.is_file():
        return exe

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        archive = td / "zig.zip"
        extract = td / "extract"

        download(ZIG_URL, archive)
        with zipfile.ZipFile(archive) as z:
            z.extractall(extract)

        source = next(p for p in extract.iterdir() if p.is_dir())
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(source), str(target))

    return exe


def run_build(zig: Path, target: str, precision: str):
    env = dict(os.environ)
    env["GODOT_CPP_ZIG"] = str(zig)

    cmd = [
        sys.executable,
        "-m",
        "SCons",
        "-f",
        "ci/SConstruct.zig",
        f"api_version={API}",
        "platform=windows",
        "arch=x86_64",
        f"target={target}",
        f"precision={precision}",
        "-j4",
    ]
    print(" ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT, env=env)


def package_precision(precision: str):
    output = ROOT / f"godot-cpp-api-{API}-windows-x86_64-zig-{precision}.zip"
    subprocess.check_call(
        [
            sys.executable,
            "scripts/package.py",
            "--source", "godot-cpp",
            "--output", str(output),
            "--api-version", API,
            "--godot-cpp-sha", REF,
            "--variant", "windows-x86_64-zig",
            "--compiler", "zig",
            "--platform", "windows",
            "--arch", "x86_64",
            "--precision", precision,
            "--zig-version", ZIG_VERSION,
        ],
        cwd=ROOT,
    )
    print("Created:", output)


def main() -> int:
    if sys.platform != "win32":
        print("ERROR: this recovery helper is intentionally Windows/Zig only.")
        return 2

    ensure_scons()
    ensure_upstream()
    zig = ensure_zig()

    for precision in ("single", "double"):
        for target in ("template_debug", "template_release"):
            run_build(zig, target, precision)
        package_precision(precision)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
