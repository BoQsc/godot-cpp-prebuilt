#!/usr/bin/env python

import os

api_version = ARGUMENTS.get("api_version", "4.7")

env = SConscript(
    "godot-cpp/SConstruct",
    {"api_version": api_version},
)

zig_exe = os.environ.get("GODOT_CPP_ZIG", "")
if not zig_exe:
    raise RuntimeError("GODOT_CPP_ZIG must point to zig.exe")

zig_exe = os.path.abspath(zig_exe)
zig_target = os.environ.get("GODOT_CPP_ZIG_TARGET", "x86_64-windows-gnu")
zig_cache = os.path.abspath(os.environ.get("ZIG_GLOBAL_CACHE_DIR", "zig_cache"))
os.makedirs(zig_cache, exist_ok=True)

if not env.get("use_mingw", False):
    raise RuntimeError("Zig build requires use_mingw=yes")

zig_q = '"{}"'.format(zig_exe)
env.Replace(
    CC=f"{zig_q} cc -target {zig_target}",
    CXX=f"{zig_q} c++ -target {zig_target}",
    LINK=f"{zig_q} c++ -target {zig_target}",
    AR=f"{zig_q} ar",
    RANLIB=f"{zig_q} ranlib",
)

env["ENV"].update(os.environ)
env["ENV"]["ZIG_GLOBAL_CACHE_DIR"] = zig_cache
env["ENV"]["ZIG_LOCAL_CACHE_DIR"] = zig_cache

print("Zig compiler:", zig_exe)
print("Zig target:", zig_target)
print("Zig cache:", zig_cache)
