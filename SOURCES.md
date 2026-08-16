# Upstream sources

This repository is intentionally a build/distribution layer around official upstream
`godot-cpp`.

Primary references:

- `godotengine/godot-cpp`
- `godotengine/godot-cpp-template`

The default pinned upstream revision is recorded in `builds.json`.

The build matrix follows the platform/toolchain patterns used by upstream godot-cpp CI,
with an additional Windows/Zig build retained from a previously working GDExtension setup.

Release packages preserve the upstream `godot-cpp` license.
