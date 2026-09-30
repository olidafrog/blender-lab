#!/usr/bin/env python3
"""What a Claude Code session cost: turns, tokens, Blender runs, reviews, models, time.

Run with plain python3 (standard library only), from the repo root:
  python3 tools/session_cost.py                 # every session of this repo, one row each
  python3 tools/session_cost.py <id|path>...    # chosen sessions (id prefix is enough)
  python3 tools/session_cost.py --latest        # the newest session (usually this one)
  python3 tools/session_cost.py --latest --scoreboard   # one line for knowledge/process/scoreboard.md

Reads ~/.claude/projects/<mangled repo path>/<session>.jsonl plus its subagents/*.jsonl.
--project-dir overrides the folder (a worktree has its own).
Tokens are summed once per API message; subagent tokens are counted apart from the main thread.
Builder is the main thread's most-used model. Reviews counts reviewer agents on any model (the final
calibration included); Reviewer is the model they were spawned with.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IDLE_GAP = 10 * 60  # seconds; longer gaps between events do not count as active time


def project_dir(repo=REPO):
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(repo))


def ts(d):
    t = d.get("timestamp")
    return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() if t else None


def read(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def usage_totals(events):
    """Sum usage once per message id (one API reply is split over several events)."""
    seen, tot = set(), dict(calls=0, out=0, inp=0, cache_read=0, cache_write=0)
    for d in events:
        if d.get("type") != "assistant":
            continue
        m = d.get("message", {})
        mid, u = m.get("id"), m.get("usage")
        if not u or mid in seen:
            continue
        seen.add(mid)
        tot["calls"] += 1
        tot["out"] += u.get("output_tokens", 0)
        tot["inp"] += u.get("input_tokens", 0)
        tot["cache_read"] += u.get("cache_read_input_tokens", 0)
        tot["cache_write"] += u.get("cache_creation_input_tokens", 0)
    return tot


def tool_uses(events):
    for d in events:
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    yield c.get("name"), c.get("input") or {}


def human_turns(events):
    n = 0
    for d in events:
        if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta"):
            continue
        origin = (d.get("origin") or {}).get("kind")
        content = d.get("message", {}).get("content")
        if origin == "human" or (origin is None and isinstance(content, str)
                                 and not content.startswith("<")):
            n += 1
    return n


def active_seconds(times):
    times = sorted(t for t in times if t)
    return sum(min(b - a, IDLE_GAP) for a, b in zip(times, times[1:]))


def experiments_touched(uses):
    names = {}
    for name, inp in uses:
        text = inp.get("file_path") or inp.get("command") or ""
        for m in re.finditer(r"experiments/([A-Za-z0-9_-]+)/", text):
            if (REPO / "experiments" / m.group(1)).is_dir():
                names[m.group(1)] = names.get(m.group(1), 0) + 1
    return sorted(names, key=names.get, reverse=True)


def best_score(exp):
    """Highest score in the experiment's PROGRESS.md table, if any."""
    p = REPO / "experiments" / exp / "PROGRESS.md"
    if not p.exists():
        return None
    best = None
    for line in p.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"\d+(\.\d+)?", cells[1]):
            best = max(best or 0.0, float(cells[1]))
    return best


def analyse(path):
    path = Path(path)
    main = list(read(path))
    sub_files = sorted((path.parent / path.stem / "subagents").glob("*.jsonl"))
    subs = [list(read(f)) for f in sub_files]
    uses = list(tool_uses(main))
    sub_uses = [u for s in subs for u in tool_uses(s)]

    blender = sum(1 for n, i in uses + sub_uses
                  if n == "Bash" and "tools/blender.sh" in (i.get("command") or ""))
    agents = [i for n, i in uses if n in ("Agent", "Task")]
    review_agents = [i for i in agents
                     if "review" in (i.get("description", "") + i.get("prompt", "")[:400]).lower()]
    reviewers = sorted({i.get("model") or "inherit" for i in review_agents})
    models = {}
    for d in main:
        m = d.get("message", {}).get("model") if d.get("type") == "assistant" else None
        if m and not m.startswith("<"):
            models[m] = models.get(m, 0) + 1
    builder = max(models, key=models.get).replace("claude-", "") if models else "?"
    review_files = {m.group(0) for n, i in uses + sub_uses if n == "Write"
                    for m in [re.search(r"reviews/review_v[^/]*\.md$", i.get("file_path", ""))] if m}
    skills = sorted({i.get("skill") for n, i in uses if n == "Skill" and i.get("skill")})
    web = sum(1 for n, _ in uses + sub_uses if n in ("WebSearch", "WebFetch"))

    times = [ts(d) for d in main]
    t = [x for x in times if x]
    m, s = usage_totals(main), usage_totals([d for sub in subs for d in sub])
    exps = experiments_touched(uses + sub_uses)
    return dict(
        session=path.stem, start=datetime.fromtimestamp(min(t)).strftime("%Y-%m-%d %H:%M") if t else "?",
        experiments=exps, turns=human_turns(main), calls=m["calls"],
        out=m["out"], cache_read=m["cache_read"], sub_out=s["out"], sub_cache_read=s["cache_read"],
        subagents=len(subs), blender=blender, reviews=len(review_agents), reviewer="/".join(reviewers) or "-",
        builder=builder, review_files=len(review_files),
        web=web, skills=skills, wall_min=(max(t) - min(t)) / 60 if t else 0,
        active_min=active_seconds(times) / 60,
        best=best_score(exps[0]) if exps else None,
    )


def k(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def row(r):
    return (f"| {r['session'][:8]} | {r['start']} | {', '.join(r['experiments'][:2]) or '-'} | {r['turns']} "
            f"| {r['builder']} | {r['calls']} | {r['blender']} | {r['reviews']} | {r['reviewer']} | {r['web']} | {k(r['out'])} "
            f"| {k(r['cache_read'])} | {k(r['sub_out'])} | {r['active_min']:.0f} / {r['wall_min']:.0f} "
            f"| {', '.join(r['skills']) or '-'} |")


HEADER = ("| Session | Start | Experiment | Turns | Builder | API calls | Blender runs | Reviews | Reviewer | Web "
          "| Output | Cache read | Subagent output | Active / wall min | Skills |\n|" + "---|" * 15)


def scoreboard(r):
    best = f"{r['best']:.1f}" if r["best"] is not None else "-"
    exp = r["experiments"][0] if r["experiments"] else "-"
    return (f"| {r['start'][:10]} | {exp} | {r['session'][:8]} | {r['builder']} | {r['reviewer']} "
            f"| {r['reviews']} | {best} "
            f"| {r['blender']} | {k(r['out'] + r['sub_out'])} | {r['active_min']:.0f} |")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sessions", nargs="*", help="session ids (prefix ok) or .jsonl paths")
    ap.add_argument("--latest", action="store_true", help="only the newest session")
    ap.add_argument("--scoreboard", action="store_true", help="print scoreboard.md lines")
    ap.add_argument("--project-dir", type=Path, default=None)
    a = ap.parse_args()

    pdir = a.project_dir or project_dir()
    files = sorted(pdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if a.sessions:
        chosen = []
        for s in a.sessions:
            p = Path(s)
            chosen += [p] if p.suffix == ".jsonl" and p.exists() else [f for f in files if f.stem.startswith(s)]
        files = chosen
    elif a.latest:
        files = files[-1:]
    if not files:
        sys.exit(f"no transcripts found in {pdir}")

    rows = [analyse(f) for f in files]
    if a.scoreboard:
        for r in rows:
            print(scoreboard(r))
        return
    print(HEADER)
    for r in rows:
        print(row(r))


if __name__ == "__main__":
    main()
