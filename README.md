# godot-cpp-prebuilt

Automated prebuilt `godot-cpp` packages for GDExtension development.

The repository builds the official `godotengine/godot-cpp` source in GitHub Actions, packages the generated bindings plus static libraries, and publishes them as GitHub Release assets.

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

```text
Godot API:        4.7
godot-cpp commit: d7b6162249ed52796a8301d216c24ee71d68c2bf
```

See `builds.json`.

## Published variants

Each package contains both `template_debug` and `template_release` libraries for exactly one precision.

Precision is deliberately separate because generated bindings are precision-specific:

```text
single
double
```

Release variants mirror the upstream `godot-cpp` SCons CI toolchains:

| Asset ID | Toolchain |
|---|---|
| `windows-x86_64-msvc` | Windows x86_64 / MSVC |
| `windows-x86_64-mingw` | Windows x86_64 / MinGW |
| `linux-x86_64-gcc` | Linux x86_64 / GCC |
| `macos-universal-clang` | macOS universal / Clang |
| `android-arm64` | Android arm64 |
| `ios-arm64` | iOS arm64 |
| `web-wasm32` | Web / Wasm |

That is 7 platform/toolchain variants × 2 precisions = 14 release packages.

## Build a release

1. Open **Actions**.
2. Select **Build and release godot-cpp**.
3. Click **Run workflow**.
4. Keep the defaults for the first build.
5. Set **Publish GitHub Release** to `true` when you want a release.

A default release tag looks like:

```text
api-4.7-d7b6162
```

Example assets:

```text
godot-cpp-api-4.7-windows-x86_64-msvc-single.zip
godot-cpp-api-4.7-windows-x86_64-msvc-double.zip
godot-cpp-api-4.7-windows-x86_64-mingw-single.zip
godot-cpp-api-4.7-linux-x86_64-gcc-single.zip
godot-cpp-api-4.7-macos-universal-clang-single.zip
godot-cpp-api-4.7-android-arm64-single.zip
godot-cpp-api-4.7-ios-arm64-single.zip
godot-cpp-api-4.7-web-wasm32-single.zip
... matching -double.zip assets
manifest.json
```

## Use from another GitHub workflow

```yaml
- name: Download prebuilt godot-cpp
  uses: OWNER/godot-cpp-prebuilt@main
  with:
    api-version: "4.7"
    precision: single
    path: godot-cpp

- name: Build my GDExtension
  run: scons build_library=no api_version=4.7 precision=single
```

On Windows, `variant: auto` selects `windows-x86_64-msvc`.

## Local download

```text
python scripts/install.py --repo OWNER/godot-cpp-prebuilt --api-version 4.7
```

## Consumer SCons

Typical integration:

```python
env = SConscript("godot-cpp/SConstruct", {"api_version": "4.7"})
```

Then build against the downloaded package without rebuilding `godot-cpp`:

```text
scons build_library=no api_version=4.7 precision=single
```

Use `precision=double` only with the matching `-double.zip` package and a double-precision Godot build.

## Double precision

The release workflow does not fake double precision from the normal API file. It builds a real Godot editor with `precision=double`, dumps its GDExtension API, verifies the API reports double precision, and reuses that API for all double packages.

## Smoke test and release gate

After all 14 packages build, CI downloads the fresh Linux GCC single and double packages, builds a tiny GDExtension using `build_library=no`, and loads it in matching Godot editors. Release publishing depends on those smoke tests succeeding.

## Local recovery build

`local_build.py` is a Windows/MSVC recovery helper. It builds the single-precision MSVC package locally. Double precision is attempted only when `GODOT_CPP_DOUBLE_API` points to a genuine API dump from a double-precision Godot editor.

## Not an official Godot repository

This repository builds and redistributes artifacts from the official MIT-licensed `godotengine/godot-cpp` project. It is not maintained or endorsed by the Godot Engine project.
