"""Assemble one review round's prompt: REVIEWER_PROMPT.md + render, crop and reference paths.

    python3 tools/review_prompt.py <experiment> <vNN>        # prints the prompt

`tools/review_round.py` calls this and saves the prompt; run this alone only to look at one.
Run tools/crops.py first so reviews/crops_<vNN>/ exists.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONLY = ("Use only the files listed here and the measurement script the brief names. Do not open any other file in the "
        "repository: no earlier reviews, progress notes, build scripts or snapshots.")


def p(f):
    return Path(f).resolve().as_posix()


def references(exp):
    return ["References:"] + [f"- {p(f)}" for f in sorted((exp / "references").iterdir())
                              if f.is_file() and not f.name.startswith(".")]


def build(name, v):
    exp = ROOT / "experiments" / name
    lines = [(exp / "reviews" / "REVIEWER_PROMPT.md").read_text(encoding="utf-8"), "",
             f"Render: {p(exp / 'renders' / f'{v}.png')}", "Crops:"]
    lines += [f"- {p(f)}" for f in sorted((exp / "reviews" / f"crops_{v}").glob("*.png"))]
    lines += references(exp)
    lines += ["", ONLY, f"Write your review to `{p(exp / 'reviews' / f'review_{v}.md')}`."]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(build(sys.argv[1], sys.argv[2]))
