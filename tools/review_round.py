#!/usr/bin/env python3
"""One review round in one command: budget, preflight, pixel gate, crops, snapshot, prompt.

Plain python3, from the repo root:
  python3 tools/review_round.py <experiment> <vNN> [x,y ...]        # prepare the round for renders/<vNN>.png
  python3 tools/review_round.py <experiment> --pair <A> <B> [--name calibration]   # blind pair

A round does, in order, and stops at the first that fails:
  1. Budget: counts reviews/review_v*.md against the Budget in BRIEF.md.
  2. Round 1 only (or the first review of a round: "## Round ... (from vNN)" in PROGRESS.md):
     reviews/preflight_*.png must exist (build.py --preflight), or PROGRESS.md says "preflight skipped: <why>";
     with photo references, RESEARCH.md or PROGRESS.md must mention their sharpness (tools/sharpness.py).
  3. Gate: tools/metrics.py between the last reviewed render and this one, with the x,y points as
     target crops. NO CHANGE stops the round.
  4. Crops into reviews/crops_<vNN>/: round 1 gets the centre and quadrants plus the points; later
     rounds get only the points (the area you changed and what the last review flagged), so at
     least one point is required.
  5. Snapshot scripts/build.py and the local modules it imports, in any subfolder, to snapshots/ (never reviews/).
  6. Writes reviews/prompt_<vNN>.txt and prints the one line to give the reviewer.

Options: --with-prev (round 2 on) adds a blind pair: this render and the last reviewed one as P.png and
Q.png in random order in reviews/pair_<vNN>/, key in snapshots/; the reviewer brief's Pairwise section
asks which is closer. --force skips the gate verdict (the change is outside the crops, or the previous review
was of another preset). --all-crops gives a later round the full crop set.

--pair copies two renders to neutral names (A.png, B.png, random order) in reviews/<name>/ and
writes reviews/prompt_<name>.txt. The key goes to snapshots/<name>_key.txt, where the reviewer is
told not to look. <A> and <B> are version names in this experiment, or paths to any PNG.
"""
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_prompt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def stop(msg, code=2):
    print(f"[round] STOP: {msg}")
    sys.exit(code)


def budget(exp):
    m = re.search(r"^##\s*Budget\s*\n+(.*)", (exp / "BRIEF.md").read_text(encoding="utf-8"), re.M)
    n = re.search(r"\d+", m.group(1)) if m else None
    return int(n.group(0)) if n else 10


def blender(*args):
    r = subprocess.run([str(ROOT / "tools" / "blender.sh"), *map(str, args)], cwd=ROOT,
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    if r.returncode:
        print(out)
        stop(f"tools/blender.sh {args[0]} failed")
    return out


def snapshot(exp, v):
    """build.py and every local module it imports, directly or through another, in any subfolder of scripts/."""
    snaps = exp / "snapshots"
    snaps.mkdir(exist_ok=True)
    build = exp / "scripts" / "build.py"
    files = {f.stem: f for f in sorted((exp / "scripts").rglob("*.py")) if "__pycache__" not in f.parts}
    keep, todo = {"build"}, [build]
    while todo:
        src = todo.pop().read_text(encoding="utf-8")
        for stem, f in files.items():
            if stem not in keep and re.search(rf"^\s*(import|from)\s+{re.escape(stem)}\b", src, re.M):
                keep.add(stem)
                todo.append(f)
    made = []
    for stem in sorted(keep):
        shutil.copyfile(files[stem], snaps / f"{stem}_{v}.py")
        made.append(f"{stem}_{v}.py")
    return made


def round_(name, v, points, force, all_crops, with_prev=False):
    exp = ROOT / "experiments" / name
    render = exp / "renders" / f"{v}.png"
    if not render.exists():
        stop(f"no render at {render}")
    if not (exp / "reviews" / "REVIEWER_PROMPT.md").exists():
        stop("reviews/REVIEWER_PROMPT.md is missing. Fill it from the template first (review-render step 2).")
    reviews = sorted((exp / "reviews").glob("review_v*.md"), key=lambda f: f.stat().st_mtime)
    done, cap = len(reviews), budget(exp)
    progress = (exp / "PROGRESS.md").read_text(encoding="utf-8") if (exp / "PROGRESS.md").exists() else ""
    # a long-running experiment works in rounds ("## Round three: the sofa (from v19)" in PROGRESS.md);
    # the first review of a round gets the round-1 checks
    starts = re.findall(r"^##\s*Round\b[^\n]*\(from v(\d+)\)", progress, re.M | re.I)
    since = int(starts[-1]) if starts else 0
    in_round = [f for f in reviews if (m := re.match(r"review_v(\d+)", f.name)) and int(m.group(1)) >= since]
    if (exp / "reviews" / f"review_{v}.md").exists():
        stop(f"{v} already has a review")
    if done >= cap:
        stop(f"budget spent ({done} of {cap} reviews). Go to Stopping in review-render.")
    first = not in_round
    print(f"[round] {name} {v}: review {done + 1} of {cap}")

    if first:
        if not list((exp / "reviews").glob("preflight*.png")) and not re.search(r"preflight skipped", progress, re.I):
            stop("no preflight sheet. Run build.py --preflight and read it before round 1, "
                 "or write 'preflight skipped: <why>' in PROGRESS.md.")
        # a photo reference is a processing chain: a soft render beside a sharpened JPEG reads CG everywhere
        # (aztechno-building; apartment-model rounds one to three never measured it)
        research = (exp / "RESEARCH.md").read_text(encoding="utf-8") if (exp / "RESEARCH.md").exists() else ""
        photos = [f for f in (exp / "references").rglob("*") if f.suffix.lower() in (".jpg", ".jpeg", ".heic")]
        if photos and not re.search(r"sharpness", research + progress, re.I):
            stop("the references include photos, but RESEARCH.md and PROGRESS.md never mention sharpness. "
                 "Run tools/sharpness.py <photo> <render> (and tools/photo_finish.py if the render is softer), "
                 "or write 'sharpness skipped: <why>' in PROGRESS.md.")
    else:
        if not points and not all_crops:
            stop("a later round needs at least one x,y: the area you changed and each area the last review "
                 "flagged (--all-crops for the full set).")
        prev = exp / "renders" / (reviews[-1].stem.replace("review_", "") + ".png")
        if prev.exists() and prev != render:
            out = blender("tools/metrics.py", prev, render, *points)
            print("\n".join(line for line in out.splitlines() if "[out]" in line))
            if "NO CHANGE" in out and not force:
                stop("the change did not reach the pixels. Fix that and render again (--force to override).", 3)

    crops = exp / "reviews" / f"crops_{v}"
    shutil.rmtree(crops, ignore_errors=True)
    flag = [] if first or all_crops else ["--only-points"]
    blender("tools/crops.py", render, 512, crops, *flag, *points)
    print(f"[round] crops: {len(list(crops.glob('*.png')))} in {crops.relative_to(ROOT)}")
    print(f"[round] snapshot: {', '.join(snapshot(exp, v))}")

    text = review_prompt.build(name, v)
    if with_prev and not first and prev.exists():
        d = exp / "reviews" / f"pair_{v}"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        srcs = [render, prev]
        random.shuffle(srcs)
        for label, f in zip("PQ", srcs):
            shutil.copyfile(f, d / f"{label}.png")
        (exp / "snapshots" / f"pair_{v}_key.txt").write_text(
            "".join(f"{label} = {f.relative_to(ROOT).as_posix()}\n" for label, f in zip("PQ", srcs)), encoding="utf-8")
        text = text.replace("\nReferences:", f"\nPair folder (Pairwise section): {review_prompt.p(d / 'P.png')}, "
                                              f"{review_prompt.p(d / 'Q.png')}\nReferences:", 1)
        print(f"[round] pair: reviews/pair_{v}/ (key in snapshots/pair_{v}_key.txt)")
    prompt = exp / "reviews" / f"prompt_{v}.txt"
    prompt.write_text(text, encoding="utf-8")
    print(f"[round] READY. Spawn a fresh Opus reviewer (Agent, model: opus) with exactly this prompt:\n"
          f"Your brief is in {prompt.as_posix()}. Read it and follow it exactly.")


def pair(name, a, b, tag):
    exp = ROOT / "experiments" / name

    def find(x):
        f = Path(x) if "/" in x else exp / "renders" / f"{x}.png"
        f = f if f.is_absolute() else (ROOT / f if "/" in x else f)
        if not f.exists():
            stop(f"no render at {f}")
        return f

    srcs = [find(a), find(b)]
    random.shuffle(srcs)
    d = exp / "reviews" / tag
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    for label, f in zip("AB", srcs):
        shutil.copyfile(f, d / f"{label}.png")  # a fresh copy: no version in the name, no telling mtime
    (exp / "snapshots").mkdir(exist_ok=True)
    key = exp / "snapshots" / f"{tag}_key.txt"
    key.write_text("".join(f"{label} = {f.relative_to(ROOT).as_posix()}\n" for label, f in zip("AB", srcs)),
                   encoding="utf-8")
    out = exp / "reviews" / f"{tag}.md"
    lines = [(exp / "reviews" / "REVIEWER_PROMPT.md").read_text(encoding="utf-8"), "",
             "Two renders follow, labelled A and B. Review each against the brief and references in the format "
             "above (score, targets, top problem), each on its own merits. Then say in two sentences which is "
             "closer to the reference and why.",
             f"A: {review_prompt.p(d / 'A.png')}", f"B: {review_prompt.p(d / 'B.png')}",
             *review_prompt.references(exp), "", review_prompt.ONLY,
             f"Write your review to `{review_prompt.p(out)}`."]
    prompt = exp / "reviews" / f"prompt_{tag}.txt"
    prompt.write_text("\n".join(lines), encoding="utf-8")
    print(f"[round] pair ready; key in {key.relative_to(ROOT)} (read it only after the review).\n"
          f"[round] READY. Spawn a fresh Opus reviewer (Agent, model: opus) with exactly this prompt:\n"
          f"Your brief is in {prompt.as_posix()}. Read it and follow it exactly.")


if __name__ == "__main__":
    argv = sys.argv[1:]
    flags = {f for f in ("--force", "--all-crops", "--with-prev") if f in argv}
    argv = [a for a in argv if a not in flags]
    tag = "calibration"
    if "--name" in argv:
        i = argv.index("--name")
        tag = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) >= 4 and argv[1] == "--pair":
        if (ROOT / "experiments" / argv[0] / "reviews" / f"{tag}.md").exists():
            tag = f"{tag}_{argv[2]}"         # a second calibration (a new brief or series) keeps the first one
        pair(argv[0], argv[2], argv[3], tag)
    elif len(argv) >= 2 and not argv[1].startswith("--"):
        round_(argv[0], argv[1], argv[2:], "--force" in flags, "--all-crops" in flags, "--with-prev" in flags)
    else:
        sys.exit(__doc__)
