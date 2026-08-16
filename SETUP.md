# Repository setup

This file is meant to be read once when creating the GitHub repository.

## Recommended repository name

**Recommended:**

```text
godot-cpp-prebuilt
```

Why:

- says exactly what the repository provides,
- does not sound like an official Godot repository,
- remains useful beyond one project,
- does not tie the repository to World or another addon.

Alternative:

```text
godot-cpp-binaries
```

I prefer `godot-cpp-prebuilt`.

There is already third-party use of the name `godot-cpp-builds`, so using a distinct name
avoids unnecessary ambiguity.

## GitHub description

Recommended:

> Prebuilt godot-cpp libraries for GDExtension development, built automatically for common platforms and Godot APIs.

Shorter:

> Automated prebuilt godot-cpp libraries for GDExtension development.

## Website

Optional:

```text
https://github.com/godotengine/godot-cpp
```

This makes the upstream project obvious.

## Topics

Recommended GitHub topics:

```text
godot
godot-engine
godot-cpp
gdextension
cpp
prebuilt
bindings
github-actions
game-development
```

## Visibility

Recommended:

```text
Public
```

The releases are intended to be reusable build infrastructure.

## License

This repository uses:

```text
MIT
```

The upstream `godot-cpp` project is also MIT licensed.

Release packages preserve the upstream license file.

## Default branch

```text
main
```

## First upload

Upload the contents of this ZIP as the repository root.

The result should start like:

```text
.github/
scripts/
action.yml
builds.json
README.md
SETUP.md
LICENSE
...
```

Do **not** upload an extra enclosing `godot-cpp-prebuilt/` directory if GitHub's web uploader
would make it a nested folder.

## GitHub Actions permissions

The release workflow requires permission to create releases and upload assets.

The workflow already declares:

```yaml
permissions:
  contents: write
```

If your repository has restrictive organization-level policy, ensure GitHub Actions is
allowed to write repository contents.

## First release

Go to:

```text
Actions
→ Build and release godot-cpp
→ Run workflow
```

Use:

```text
Godot API:             4.7
godot-cpp ref:         leave default
Publish GitHub Release true
Release tag:           leave blank
```

The workflow resolves the ref to a commit and generates a deterministic tag.

## Release naming

Recommended release tag format:

```text
api-{GODOT_API}-{SHORT_GODOT_CPP_SHA}
```

Example:

```text
api-4.7-d7b6162
```

Do not call releases simply `4.7.1`.

The binaries are primarily identified by:

```text
Godot API
godot-cpp source revision
toolchain
platform
architecture
precision
target
```

not by one Godot patch version.

## Asset naming

Keep the generated names:

```text
godot-cpp-api-4.7-windows-x86_64-msvc-single.zip
godot-cpp-api-4.7-windows-x86_64-msvc-double.zip
godot-cpp-api-4.7-windows-x86_64-mingw-single.zip
godot-cpp-api-4.7-windows-x86_64-zig-single.zip
godot-cpp-api-4.7-linux-x86_64-gcc-single.zip
...
```

Each package contains debug and release libraries for exactly one precision. Precision
is encoded in the asset name because generated bindings are precision-specific.

## About the Zig build

The Zig Windows build is intentionally retained because the known working GDExtension
setup used Zig as:

```text
CC      zig cc
CXX     zig c++
LINK    zig c++
AR      zig ar
RANLIB  zig ranlib
```

with dedicated Zig cache directories.

MSVC and MinGW builds are also published so this repository is not tied to Zig.

## Updating godot-cpp

Do not silently change the source revision in an existing release.

Instead:

1. update `builds.json`,
2. run `python scripts/check_config.py`,
3. commit the change,
4. run a new Build and Release workflow,
5. publish a new release.

## Updating to a new Godot API

Verify that the selected upstream `godot-cpp` revision actually includes that API version.
Then update `builds.json` and create a new release.

## Repository About text

Suggested final GitHub About panel:

**Description**

> Prebuilt godot-cpp libraries for GDExtension development, built automatically for common platforms and Godot APIs.

**Website**

> https://github.com/godotengine/godot-cpp

**Topics**

> godot, godot-engine, godot-cpp, gdextension, cpp, prebuilt, bindings, github-actions, game-development

Precision is encoded in each asset filename.
