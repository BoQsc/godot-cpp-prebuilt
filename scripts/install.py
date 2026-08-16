#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile


def host_variant() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows" and machine in {"amd64", "x86_64"}:
        return "windows-x86_64-msvc"
    if system == "linux" and machine in {"amd64", "x86_64"}:
        return "linux-x86_64-gcc"
    if system == "darwin":
        return "macos-universal-clang"

    raise RuntimeError(
        f"No automatic prebuilt variant for host {platform.system()} {platform.machine()}."
    )


def github_json(url: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "godot-cpp-prebuilt-installer",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def find_release(repo: str, api_version: str, tag: str | None, token: str | None):
    if tag:
        return github_json(
            f"https://api.github.com/repos/{repo}/releases/tags/{urllib.parse.quote(tag)}",
            token,
        )

    releases = github_json(
        f"https://api.github.com/repos/{repo}/releases?per_page=100",
        token,
    )
    prefix = f"api-{api_version}-"

    for release in releases:
        if release.get("draft"):
            continue
        if str(release.get("tag_name", "")).startswith(prefix):
            return release

    raise RuntimeError(f"No published release found for Godot API {api_version}.")


def download_asset(asset: dict, output: Path, token: str | None):
    headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "godot-cpp-prebuilt-installer",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(asset["url"], headers=headers)
    with urllib.request.urlopen(request) as response, output.open("wb") as f:
        shutil.copyfileobj(response, f)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=os.environ.get("GODOT_CPP_PREBUILT_REPO", ""))
    p.add_argument("--api-version", default="4.7")
    p.add_argument("--variant", default="auto")
    p.add_argument("--precision", default="single", choices=("single", "double"))
    p.add_argument("--release")
    p.add_argument("--path", default="godot-cpp")
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    args = p.parse_args()

    if not args.repo:
        print("ERROR: --repo OWNER/REPOSITORY is required.")
        return 2

    variant = host_variant() if args.variant == "auto" else args.variant
    asset_name = f"godot-cpp-api-{args.api_version}-{variant}-{args.precision}.zip"

    try:
        release = find_release(args.repo, args.api_version, args.release, args.token)
    except (RuntimeError, urllib.error.HTTPError) as exc:
        print("ERROR:", exc)
        return 3

    asset = next(
        (item for item in release.get("assets", []) if item.get("name") == asset_name),
        None,
    )
    if not asset:
        print(f"ERROR: release {release.get('tag_name')} has no asset {asset_name}")
        return 4

    destination = Path(args.path).resolve()

    with tempfile.TemporaryDirectory(prefix="godot-cpp-prebuilt-") as td:
        td = Path(td)
        archive_path = td / asset_name
        extract_path = td / "extract"

        print(f"Downloading {asset_name} from {release.get('tag_name')}...")
        download_asset(asset, archive_path, args.token)

        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(extract_path)

        source = extract_path / "godot-cpp"
        if not source.is_dir():
            print("ERROR: downloaded asset is missing godot-cpp/")
            return 5

        if destination.exists():
            shutil.rmtree(destination)

        shutil.copytree(source, destination)

    print("Installed:", destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
