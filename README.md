# godot-cpp-prebuilt

Automated prebuilt `godot-cpp` packages for GDExtension development.

The repository builds the official `godotengine/godot-cpp` source in GitHub Actions,
packages the generated bindings plus static libraries, and publishes them as GitHub
Release assets.

The normal consumer path is:

```text
GitHub Actions builds godot-cpp once
        ↓
GitHub Release asset
        ↓
download/extract in GDExtension project
        ↓
build only your extension
```

Local `godot-cpp` compilation remains available as a recovery option.

## Default build

The repository currently pins:

```text
Godot API:        4.7
godot-cpp commit: d7b6162249ed52796a8301d216c24ee71d68c2bf
Zig:              0.16.0-dev.1484+d0ba6642b
```

The pinned `godot-cpp` commit is a current 10.x commit that includes Godot 4.7 API support.

See `builds.json`.

## Published variants

Each package contains both:

```text
template_debug
template_release
```

Precision is deliberately a separate package because generated bindings are precision-specific:

```text
single
double
```

Default release variants:

| Asset ID | Toolchain |
|---|---|
| `windows-x86_64-msvc` | Windows x86_64 / MSVC |
| `windows-x86_64-mingw` | Windows x86_64 / MinGW |
| `windows-x86_64-zig` | Windows x86_64 / pinned Zig |
| `linux-x86_64-gcc` | Linux x86_64 / GCC |
| `macos-universal-clang` | macOS universal / Clang |
| `android-arm64` | Android arm64 |
| `ios-arm64` | iOS arm64 |
| `web-wasm32` | Web / Wasm |

## Build a release

After uploading this repository to GitHub:

1. Open **Actions**.
2. Select **Build and release godot-cpp**.
3. Click **Run workflow**.
4. Keep the defaults for the first build.
5. Set **Publish GitHub Release** to `true`.

The workflow resolves the configured upstream ref to an exact commit before compiling.

A default release tag looks like:

```text
api-4.7-d7b6162
```

Assets look like:

```text
godot-cpp-api-4.7-windows-x86_64-msvc-single.zip
godot-cpp-api-4.7-windows-x86_64-msvc-double.zip
godot-cpp-api-4.7-windows-x86_64-mingw-single.zip
godot-cpp-api-4.7-windows-x86_64-zig-single.zip
godot-cpp-api-4.7-linux-x86_64-gcc-single.zip
godot-cpp-api-4.7-macos-universal-clang-single.zip
godot-cpp-api-4.7-android-arm64-single.zip
godot-cpp-api-4.7-ios-arm64-single.zip
godot-cpp-api-4.7-web-wasm32-single.zip
... matching -double.zip assets
manifest.json
```

## Use from another GitHub workflow

This repository is also a composite GitHub Action.

```yaml
- name: Download prebuilt godot-cpp
  uses: OWNER/godot-cpp-prebuilt@main
  with:
    api-version: "4.7"
    precision: single
    path: godot-cpp

- name: Build my GDExtension
  run: scons build_library=no api_version=4.7
```

On Windows the automatic host variant is MSVC. To use the Zig build:

```yaml
- uses: OWNER/godot-cpp-prebuilt@main
  with:
    api-version: "4.7"
    variant: windows-x86_64-zig
    precision: single
    path: godot-cpp
```

## Local download

No third-party Python packages are required:

```text
python scripts/install.py --repo OWNER/godot-cpp-prebuilt --api-version 4.7
```

Example for the Zig variant:

```text
python scripts/install.py ^
  --repo OWNER/godot-cpp-prebuilt ^
  --api-version 4.7 ^
  --variant windows-x86_64-zig ^
  --precision single ^
  --path godot-cpp
```

## Consumer SCons

The downloaded package is a complete trimmed `godot-cpp` source/build tree containing
the generated bindings and matching prebuilt libraries.

Your normal extension SConstruct can still use the official integration:

```python
env = SConscript("godot-cpp/SConstruct", {"api_version": "4.7"})
```

Build with:

```text
scons build_library=no api_version=4.7
```

`build_library=no` tells `godot-cpp` to configure the extension build and link the matching
library from `godot-cpp/bin/` without recompiling `godot-cpp`.

## Local recovery build

Windows + Zig is retained as the known recovery path:

```text
python local_build.py
```

It downloads the pinned upstream source and pinned Zig compiler, then builds the same
debug/release + single/double libraries locally.

This is intentionally not the normal workflow.

## Not an official Godot repository

This repository builds and redistributes artifacts from the official MIT-licensed
`godotengine/godot-cpp` project. It is not maintained or endorsed by the Godot Engine
project.

See `SETUP.md` before creating the GitHub repository.
