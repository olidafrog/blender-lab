"""Assemble one review round's prompt: REVIEWER_PROMPT.md + render, crop and reference paths.

    python tools/review_prompt.py <experiment> <vNN>        # prints the prompt; paste it as the Agent prompt
    python tools/review_prompt.py wonder-minidisc v09 > /tmp/p.txt

Run tools/crops.py first so reviews/crops_<vNN>/ exists.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
exp, v = ROOT / "experiments" / sys.argv[1], sys.argv[2]
p = lambda f: f.resolve().as_posix()
lines = [(exp / "reviews" / "REVIEWER_PROMPT.md").read_text(encoding="utf-8"), "",
         f"Render: {p(exp / 'renders' / f'{v}.png')}", "Crops:"]
lines += [f"- {p(f)}" for f in sorted((exp / "reviews" / f"crops_{v}").glob("*.png"))]
lines += ["References:"] + [f"- {p(f)}" for f in sorted((exp / "references").iterdir()) if f.is_file()]
lines += ["", "Use only the files listed here and the measurement script the brief names. Do not open any other file in the "
          "repository: no earlier reviews, progress notes, build scripts or snapshots.",
          f"Write your review to `{p(exp / 'reviews' / f'review_{v}.md')}`."]
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(lines))
