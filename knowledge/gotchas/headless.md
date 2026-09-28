# Headless runs

Launch with `tools/blender.sh`. It handles most of the items below.

## GPU

- `--factory-startup` and `read_factory_settings()` reset preferences, and the GPU choice lives there. Call `common.enable_gpu()` after any factory reset, on every run. `scene.cycles.device = "GPU"` alone silently falls back to CPU.
- The first OptiX render in a new Blender version prints "Loading render kernels". It is cached after that. `win`
- Eevee renders headless. The engine id is `BLENDER_EEVEE_NEXT` in 4.x and `BLENDER_EEVEE` again in 5.x. Use Eevee for fast look-dev and Cycles for finals.

## Exit codes and output

- A Python error inside `-P` exits 0 by default. Pass `--python-exit-code 1` before `-P`, and still grep for `Traceback`.
- Cycles prints a line per step. Filter to `[common]`, `RENDER TIME`, `Saved`, `Error`, `Traceback`.
- A 2× render at 1024 samples takes about 6 minutes, longer than the 2-minute tool timeout. Run long renders in the background and wait for the file. `mac`
- For quick checks render at `--scale 0.5` with 128–256 samples.
- On the 3090 Ti, 1600×1280 at 512 samples with glass, volumes and 32 glossy lobes took about 1 minute; 1024 samples about 2. Test renders at 0.5 scale / 64 samples: ~15 s. `win` `minidisc`
- Use `--norender --save x.blend` to build the file without rendering. `wonder-*`

## Paths

- Opening a `.blend` by relative path with `--factory-startup` crashes Blender with `NSURL initFileURLWithPath: nil string`. Pass an absolute path; `tools/blender.sh` does this for `BLEND=`. `5.x` `mac`

- `blender -P` does not put the script's folder on `sys.path`. Scripts insert `tools/` themselves.
- `bpy.data.images.load("relative/path")` does not resolve against the shell's cwd. Pass `Path(p).resolve()`.
- Wonder scripts resolve `--out renders/x.png` against the shell's cwd. Pass an absolute path, or `cd` into the experiment first.
- After `save_as_mainfile`, call `bpy.ops.file.make_paths_relative()` and save again. Otherwise image paths are absolute and the file breaks on the other machine.
- Saving over a file makes a `.blend1` backup. Delete it after the final save.
- `tools/blender.sh` hides any line that does not match its filter. Measurement tools print with an `[out] ` prefix so their numbers get through; `compare.py`'s MAE was silently hidden before. Use `VERBOSE=1` to see everything.
- zsh does not word-split `$v`, so `for v in "a k=v k=v"; do tools/blender.sh … --set $v` passes one argument and the settings are ignored with no error. Build a `--set` array in a bash helper. `mac` `clouds`
