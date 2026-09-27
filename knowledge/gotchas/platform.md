# Platform

- **Mac:** M4 Max, Cycles on Metal, Blender 5.2 from Steam at `~/Library/Application Support/Steam/steamapps/common/Blender/Blender.app`.
- **Windows:** RTX 3090 Ti, Cycles on OptiX, Blender 4.4 from Steam at `F:\Games\SteamLibrary\steamapps\common\Blender\blender.exe`. Steam may update it.
- The Windows registry points at `C:\Program Files (x86)\Steam\steamapps\common\Blender`. That folder is stale and has no exe. If Blender moves, read `C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf` for library paths. `win`
- Run Blender from Git Bash on Windows. In Git Bash, `"$TEMP\\$name"` escaping breaks; use `cygpath -m` for forward-slash Windows paths. `win`
- In zsh, `for x in $list` does not split words. Use an array. `--set "comp={}"` needs quotes, or brace expansion eats the braces. `mac`
- The two machines run different Blender versions. A script written on one can fail on the other. See [API changes](api-changes.md).
- On Windows `python3` is the Microsoft Store stub ("Python was not found"); use `python`. Windows Python reads and writes files as cp1252, so pass `encoding="utf-8"` (or set `PYTHONUTF8=1`) on anything touching repo text. `win`
