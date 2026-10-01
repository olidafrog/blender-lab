#!/usr/bin/env python3
"""Bring values a designer changed by hand in a saved .blend back into build.py's P dict.

  python3 tools/sync_tweaks.py <experiment> [--blend <file.blend>] [--apply]

Dumps the designer-facing values (group-node inputs, Post inputs, lights, camera, view) from the edited
.blend (default output/<experiment>.blend) and from a fresh build of scripts/build.py, and lists every
value that differs. For each, it looks for the P key whose value equals the fresh build's: one match is
printed as `--set key=value` and, with --apply, rewritten in the P dict; no match or several are listed
for a hand edit (a value built by a formula, or shared by several keys). Re-render afterwards and compare.
"""
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def dump(out, blend=None, build=None):
    env = dict(os.environ)
    args = [str(ROOT / "tools" / "blender.sh"), str(ROOT / "tools" / "sync_tweaks_dump.py"), out]
    if blend:
        env["BLEND"] = str(Path(blend).resolve())
    if build:
        args += ["--build", str(build)]
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
    if not Path(out).exists():
        sys.exit(f"dump failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return json.load(open(out))


def p_dict(src):
    a = src.index("P = {")
    b = src.index("\n}\n", a)
    return ast.literal_eval(src[a + 4:b + 2]), a, b


def same(x, y):
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        return len(x) == len(y) and all(abs(float(i) - float(j)) < 1e-4 for i, j in zip(x, y))
    if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
        return abs(float(x) - float(y)) < 1e-4
    return x == y


def lit(v, like):
    if isinstance(like, tuple) or isinstance(v, list):
        return "(" + ", ".join(f"{x:g}" for x in v) + ")"
    if isinstance(like, float) or isinstance(v, float):
        return repr(round(float(v), 6))
    return repr(v)


def main():
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    name, apply = argv[0], "--apply" in argv
    exp = ROOT / "experiments" / name
    blend = argv[argv.index("--blend") + 1] if "--blend" in argv else exp / "output" / f"{name}.blend"
    build = exp / "scripts" / "build.py"
    with tempfile.TemporaryDirectory() as t:
        edited = dump(f"{t}/edited.json", blend=blend)
        fresh = dump(f"{t}/fresh.json", build=build)
    src = build.read_text(encoding="utf-8")
    P, a, b = p_dict(src)
    changes = [(k, fresh[k], v) for k, v in edited.items() if k in fresh and not same(fresh[k], v)]
    if not changes:
        print("[out] no designer changes: the .blend matches a fresh build")
        return
    body = src[a:b]
    for k, old, new in changes:
        keys = [pk for pk, pv in P.items() if same(pv, old) or (isinstance(pv, tuple) and isinstance(old, list)
                                                                and same(list(pv)[:len(old)], old))]
        if len(keys) == 1:
            pk = keys[0]
            v = lit(new, P[pk])
            print(f"[out] {k}: {old} -> {new}   --set {pk}={v}")
            if apply:
                pat = re.compile(rf'("{re.escape(pk)}":\s*)([^,#\n]+(?:\([^)]*\))?)')
                body, n = pat.subn(lambda m: m.group(1) + v, body, count=1)
                if not n:
                    print(f"[out]   could not rewrite {pk}; edit it by hand")
        else:
            print(f"[out] {k}: {old} -> {new}   P keys with the old value: {keys or 'none'} (edit by hand)")
    if apply:
        build.write_text(src[:a] + body + src[b:], encoding="utf-8")
        print(f"[out] wrote {build.relative_to(ROOT)}; rebuild and compare (tools/metrics.py)")


if __name__ == "__main__":
    main()
