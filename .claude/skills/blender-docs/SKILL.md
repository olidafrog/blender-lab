---
name: blender-docs
description: Use when writing or debugging Blender Python (bpy) in blender-lab and unsure of an exact name — a node socket, enum value, property, operator or node type — or when an API call fails with "not found", "has no attribute", "enum ... not found", or behaves differently between Blender 4.4 and 5.x. Also use when looking for how a Blender feature, node or technique works, or what changed in a recent version.
---

# Blender docs (local)

A local copy of the Blender docs lives in `reference/` (not in git). Look things up there before guessing from memory. Training knowledge lags Blender releases, and API names change between versions.

If `reference/` is missing or has no dump for the Blender you are running, build it: `tools/fetch_docs.sh` (a few minutes). The dump alone: `tools/blender.sh tools/dump_api.py` (seconds).

## Where to look, in order

| Question | Folder | Why |
|---|---|---|
| Exact socket name, enum value, property, range, default | `reference/api-dump-<ver>/` | Dumped from the installed Blender. Ground truth for that version. |
| How to use an API, examples | `reference/api-docs-<ver>/` | Official Python API docs as text. |
| What a node or feature does, how to set it up | `reference/manual/manual/` | Blender user manual source (`.rst`). |
| What is new or changed, and when | `reference/dev-docs/docs/release_notes/<ver>/` | Release notes per version. |

`<ver>` is `5.2` on the Mac and `4.4` on Windows. Check the one you run: `tools/blender.sh` prints it.

## Recipes

```bash
D=reference/api-dump-5.2
cat $D/nodes/CompositorNodeTree/CompositorNodeGlare.txt     # sockets of one node
grep -rl "Dispersion" $D/nodes/                              # which nodes have a socket
grep -h "file_format" $D/types/ImageFormatSettings.txt       # allowed enum values
grep -ril "manifold" reference/manual/manual/render/cycles/  # a feature in the manual
grep -rl "compositor" reference/dev-docs/docs/release_notes/5.0/   # what changed
diff <(ls reference/api-dump-4.4/types) <(ls reference/api-dump-5.2/types)  # removed/added types
```

## Rules

- Check socket and enum names in the dump before you write them. Use the identifier in `[brackets]` when names collide or are ambiguous.
- Some enums depend on context: the dump shows all values, a given node may accept fewer (the File Output node takes only `OPEN_EXR_MULTILAYER`). If Blender rejects one, the error lists the allowed values.
- When the docs and the dump disagree, the dump wins for that version.
- When a lookup saves you from a trap, add it to `knowledge/gotchas/`.
