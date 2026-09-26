"""Dump the Python API of the installed Blender to plain text, exact for this version.

Run:  tools/blender.sh tools/dump_api.py
Writes reference/api-dump-<version>/:
  types/<Class>.txt        every bpy.types class: properties (type, enum values, range,
                           default), functions and their parameters
  nodes/<Tree>/<Node>.txt  every node for Shader / Compositor / Geometry trees, with its
                           input and output sockets (names, types, defaults) — RNA alone
                           does not list sockets
  INDEX.txt                one line per file
"""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
VER = ".".join(map(str, bpy.app.version[:2]))
OUT = ROOT / "reference" / f"api-dump-{VER}"


def fmt_prop(p):
    t = p.type
    bits = [f"{p.identifier}: {t}"]
    if t == "ENUM":
        items = [i.identifier for i in p.enum_items] or ["(dynamic)"]
        bits.append(("flag set of " if p.is_enum_flag else "one of ") + ", ".join(items))
    elif t == "POINTER" or t == "COLLECTION":
        bits.append(f"-> {p.fixed_type.identifier}")
    elif t in ("INT", "FLOAT"):
        if getattr(p, "array_length", 0):
            bits.append(f"[{p.array_length}]")
        bits.append(f"range {p.hard_min:g}..{p.hard_max:g}")
        try:
            d = p.default_array if p.array_length else p.default
            bits.append(f"default {tuple(d) if p.array_length else d}")
        except Exception:
            pass
        if t == "FLOAT" and p.subtype != "NONE":
            bits.append(f"subtype {p.subtype}")
    elif t == "BOOLEAN":
        bits.append(f"default {p.default}")
    elif t == "STRING":
        bits.append(f"default {p.default!r}")
    if p.is_readonly:
        bits.append("READ-ONLY")
    line = " | ".join(bits)
    return line + (f"\n      {p.description}" if p.description else "")


def dump_type(cls):
    rna = cls.bl_rna
    base = rna.base.identifier if rna.base else ""
    lines = [f"# {rna.identifier}" + (f"  (base: {base})" if base else ""), rna.description or "", "", "## Properties"]
    inherited = {p.identifier for p in rna.base.properties} if rna.base else set()
    for p in rna.properties:
        if p.identifier in ("rna_type",) or p.identifier in inherited:
            continue
        lines.append("- " + fmt_prop(p))
    funcs = [f for f in rna.functions if not (rna.base and f.identifier in {g.identifier for g in rna.base.functions})]
    if funcs:
        lines += ["", "## Functions"]
        for f in funcs:
            params = ", ".join(p.identifier + ("" if p.is_required else "=…") for p in f.parameters if not p.is_output)
            outs = [p.identifier for p in f.parameters if p.is_output]
            lines.append(f"- {f.identifier}({params})" + (f" -> {', '.join(outs)}" if outs else ""))
            if f.description:
                lines.append(f"      {f.description}")
    return "\n".join(lines) + "\n"


def sock_line(s):
    d = ""
    if hasattr(s, "default_value"):
        try:
            v = s.default_value
            v = tuple(round(x, 4) for x in v) if hasattr(v, "__len__") and not isinstance(v, str) else v
            d = f" = {v}"
        except Exception:
            pass
    return f"- [{s.identifier}] {s.name!r}: {s.bl_idname}{d}"


def dump_nodes(tree_type, prefixes):
    tree = bpy.data.node_groups.new("dump", tree_type)
    out = OUT / "nodes" / tree_type
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for name in sorted(dir(bpy.types)):
        if not name.startswith(prefixes):
            continue
        try:
            n = tree.nodes.new(name)
        except Exception:
            continue
        lines = [f"# {name}  ({n.bl_label})", (n.bl_description or "").strip(), "",
                 "## Inputs"] + [sock_line(s) for s in n.inputs] + ["", "## Outputs"] + [sock_line(s) for s in n.outputs]
        (out / f"{name}.txt").write_text("\n".join(lines) + "\n")
        names.append(f"nodes/{tree_type}/{name}.txt  {n.bl_label}")
        tree.nodes.remove(n)
    bpy.data.node_groups.remove(tree)
    return names


def main():
    (OUT / "types").mkdir(parents=True, exist_ok=True)
    index = [f"Blender {bpy.app.version_string} API dump. grep this folder; one file per class or node.", ""]
    for name in sorted(dir(bpy.types)):
        cls = getattr(bpy.types, name)
        if not hasattr(cls, "bl_rna"):
            continue
        try:
            (OUT / "types" / f"{name}.txt").write_text(dump_type(cls))
            index.append(f"types/{name}.txt  {(cls.bl_rna.description or '').splitlines()[0][:90] if cls.bl_rna.description else ''}")
        except Exception as e:
            print(f"skip {name}: {e}", file=sys.stderr)
    index += dump_nodes("ShaderNodeTree", ("ShaderNode",))
    index += dump_nodes("CompositorNodeTree", ("CompositorNode", "ShaderNode"))
    index += dump_nodes("GeometryNodeTree", ("GeometryNode", "FunctionNode", "ShaderNode"))
    (OUT / "INDEX.txt").write_text("\n".join(index) + "\n")
    print(f"Saved {OUT} ({len(index)} entries) OK")


main()
