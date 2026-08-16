# Consuming a prebuilt package

## Why the package contains more than a `.lib` or `.a`

A useful `godot-cpp` SDK needs:

```text
headers
generated bindings
GDExtension interface/API files
matching static libraries
build configuration files
```

The release package therefore contains a trimmed but usable `godot-cpp` tree.

## SCons

Typical extension SConstruct:

```python
env = SConscript("godot-cpp/SConstruct", {"api_version": "4.7"})
env.Append(CPPPATH=["src/"])

sources = Glob("src/*.cpp")
library = env.SharedLibrary(
    "bin/my_extension{}{}".format(env["suffix"], env["SHLIBSUFFIX"]),
    source=sources,
)

Default(library)
```

Then build using the prebuilt library:

```text
scons build_library=no api_version=4.7
```

The important option is:

```text
build_library=no
```

The upstream SConstruct still configures the correct platform/compiler flags and adds the
matching static library from `godot-cpp/bin`, but does not rebuild `godot-cpp`.

## Precision

Single precision:

```text
scons build_library=no api_version=4.7 precision=single
```

Double precision:

```text
scons build_library=no api_version=4.7 precision=double
```

Use the `-single.zip` package for a normal Godot build and the `-double.zip` package for
a double-precision Godot build.

## Debug / release

Editor and debug templates:

```text
target=template_debug
```

Release templates:

```text
target=template_release
```

Both libraries are included.

## Toolchain matching

Use a package built for the same toolchain family as your extension.

Examples:

```text
MSVC extension  → windows-x86_64-msvc
MinGW extension → windows-x86_64-mingw
Zig setup       → windows-x86_64-zig
```

Do not assume arbitrary C++ ABIs are interchangeable.

## GitHub Action

```yaml
- uses: OWNER/godot-cpp-prebuilt@main
  with:
    api-version: "4.7"
    variant: windows-x86_64-msvc
    precision: single
    path: godot-cpp
```

`variant: auto` chooses the ordinary host variant:

```text
Windows → windows-x86_64-msvc
Linux   → linux-x86_64-gcc
macOS   → macos-universal-clang
```
