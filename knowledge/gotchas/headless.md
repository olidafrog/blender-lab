# Headless runs

Launch with `tools/blender.sh`. It handles most of the items below.

## GPU

- `--factory-startup` and `read_factory_settings()` reset preferences, and the GPU choice lives there. Call `common.enable_gpu()` after any factory reset, on every run. `scene.cycles.device = "GPU"` alone silently falls back to CPU.
- The first OptiX render in a new Blender version prints "Loading render kernels". It is cached after that. `win`
- Eevee renders headless. In 4.x the engine id is `BLENDER_EEVEE_NEXT`; `BLENDER_EEVEE` does not exist. Use Eevee for fast look-dev and Cycles for finals. `4.4`

## Exit codes and output

- A Python error inside `-P` exits 0 by default. Pass `--python-exit-code 1` before `-P`, and still grep for `Traceback`.
- Cycles prints a line per step. Filter to `[common]`, `RENDER TIME`, `Saved`, `Error`, `Traceback`.
- A 2× render at 1024 samples takes about 6 minutes, longer than the 2-minute tool timeout. Run long renders in the background and wait for the file. `mac`
- For quick checks render at `--scale 0.5` with 128–256 samples.
- Use `--norender --save x.blend` to build the file without rendering. `wonder-*`

## Paths

- `blender -P` does not put the script's folder on `sys.path`. Scripts insert `tools/` themselves.
- `bpy.data.images.load("relative/path")` does not resolve against the shell's cwd. Pass `Path(p).resolve()`.
- Wonder scripts resolve `--out renders/x.png` against the shell's cwd. Pass an absolute path, or `cd` into the experiment first.
- After `save_as_mainfile`, call `bpy.ops.file.make_paths_relative()` and save again. Otherwise image paths are absolute and the file breaks on the other machine.
- Saving over a file makes a `.blend1` backup. Delete it after the final save.
