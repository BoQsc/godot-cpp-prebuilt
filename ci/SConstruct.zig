#!/usr/bin/env python

import os
import sys

api_version = ARGUMENTS.get("api_version", "4.7")

env = SConscript(
    "godot-cpp/SConstruct",
    {"api_version": api_version},
)

project_path = os.path.abspath(os.getcwd())
zig_exe = os.environ.get("GODOT_CPP_ZIG", "")

if not zig_exe:
    raise RuntimeError("GODOT_CPP_ZIG must point to zig.exe")

zig_exe = os.path.abspath(zig_exe)

env["CC"] = zig_exe + " cc"
env["CXX"] = zig_exe + " c++"
env["LINK"] = zig_exe + " c++"
env["AR"] = zig_exe + " ar"
env["RANLIB"] = zig_exe + " ranlib"

if sys.platform == "win32":
    env["ARCOM"] = zig_exe + " ar $ARFLAGS $TARGET ${TEMPFILE('$SOURCES')}"
    env["LINKCOM"] = (
        zig_exe
        + " c++ $LINKFLAGS -o $TARGET ${TEMPFILE('$SOURCES')} $SHLINKFLAGS"
    )

zig_cache = os.path.join(project_path, "zig_cache")
os.makedirs(zig_cache, exist_ok=True)

env["ENV"]["ZIG_GLOBAL_CACHE_DIR"] = zig_cache
env["ENV"]["ZIG_LOCAL_CACHE_DIR"] = zig_cache
