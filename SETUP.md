# Repository setup

This file is meant to be read when creating or maintaining the GitHub repository.

## Recommended repository name

**`godot-cpp-prebuilt`**

Why:

- says exactly what the repository provides,
- does not sound like an official Godot repository,
- remains useful beyond one project,
- does not tie the repository to World or another addon.

Alternative: `godot-cpp-binaries`. `godot-cpp-prebuilt` is preferred.

## GitHub description

> Prebuilt godot-cpp libraries for GDExtension development, built automatically for common platforms and Godot APIs.

## Website and topics

Website: `https://github.com/godotengine/godot-cpp`

Topics: `godot`, `godot-engine`, `godot-cpp`, `gdextension`, `cpp`, `prebuilt`, `bindings`, `github-actions`, `game-development`

## Visibility and license

- Visibility: **Public**
- License: **MIT**
- Default branch: **main**

The upstream `godot-cpp` project is also MIT licensed, and release packages preserve its license file.

## First upload

Upload the repository contents at the root, not inside another enclosing directory. The root should include `.github/`, `ci/`, `scripts/`, `smoke-test/`, `action.yml`, `builds.json`, `README.md`, `SETUP.md`, and `LICENSE`.

## GitHub Actions permissions

The release workflow declares `contents: write`. If an organization policy restricts Actions, allow this workflow to create releases and upload assets.

## First release

Go to `Actions → Build and release godot-cpp → Run workflow` and use Godot API `4.7`, leave the pinned `godot-cpp` ref, enable release publishing, and leave the release tag blank.

## Release naming

Recommended tag format:

```text
api-{GODOT_API}-{SHORT_GODOT_CPP_SHA}
```

Example: `api-4.7-d7b6162`.

Do not call releases simply `4.7.1`. A package is identified by Godot API, `godot-cpp` revision, toolchain, platform, architecture, precision, and target.

## Asset naming

Examples:

```text
godot-cpp-api-4.7-windows-x86_64-msvc-single.zip
godot-cpp-api-4.7-windows-x86_64-msvc-double.zip
godot-cpp-api-4.7-windows-x86_64-mingw-single.zip
godot-cpp-api-4.7-windows-x86_64-zig-single.zip
godot-cpp-api-4.7-linux-x86_64-gcc-single.zip
```

Each package contains both `template_debug` and `template_release` libraries for exactly one precision.

## Double-precision packages

A double package must **not** be created by taking the normal single-precision `extension_api.json` and merely changing its header. `godot-cpp` intentionally rejects that mismatch.

The release workflow therefore builds one Godot editor with `precision=double`, runs `--dump-extension-api`, verifies the JSON reports `precision: double`, and reuses that genuine API for every double-precision matrix job. This happens once per workflow, not once per platform.

## Zig build

The Windows Zig variant uses stable pinned **Zig 0.16.0**, not a disappearing development snapshot. The download SHA256 is stored in `builds.json` and verified before extraction.

The compiler setup remains:

```text
CC      zig cc
CXX     zig c++
LINK    zig c++
AR      zig ar
RANLIB  zig ranlib
```

MSVC and MinGW are published alongside Zig so the repository is not tied to one Windows toolchain.

## Smoke test and release gate

After the matrix succeeds, CI downloads the fresh Linux GCC single and double packages, builds a tiny GDExtension with `build_library=no`, then loads it in the matching Godot editor. Single uses the official Godot release; double uses the double editor built earlier in the workflow.

The release job depends on those smoke tests, so a package set is not published when the consumer build/load path fails.

## Local recovery build

Normal use should be GitHub Actions plus release downloads. `local_build.py` remains a Windows/Zig recovery path.

It builds single precision normally. A local double recovery build is attempted only when `GODOT_CPP_DOUBLE_API` points to a genuine API dump from a double-precision Godot editor:

```text
set GODOT_CPP_DOUBLE_API=C:\path\to\extension_api.json
python local_build.py
```

Without that variable, the helper deliberately skips double precision instead of manufacturing an invalid package.

## Updating godot-cpp

Do not silently change the source revision in an existing release. Update `builds.json`, run `python scripts/check_config.py`, commit, run a new workflow, and publish a new release.

## Updating to a new Godot API

Verify that the selected upstream `godot-cpp` revision includes that API version. CI also expects the matching Godot stable source tag (`{API}-stable`) so it can generate the double API and run the load smoke test.
