"""Build the full reviewer request for one round: the fixed brief + paths (tools/review_prompt.py) + the
script-measured table + (from round 2) a blind pairwise pair against the best earlier render.
   python3 experiments/cyber-model/scripts/review_pack.py v03 [best_prev=v02]   > reviews/prompt_v03.txt
Order of the pair is random and unlabelled beyond X / Y; the reviewer never sees scores."""
import random
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = root.parents[1]
v = sys.argv[1]
prev = sys.argv[2] if len(sys.argv) > 2 else None
base = subprocess.run([sys.executable, str(repo / "tools/review_prompt.py"), "cyber-model", v], capture_output=True, text=True, check=True).stdout
table = subprocess.run([sys.executable, str(root / "scripts/measure.py"), str(root / f"renders/{v}.png"), "--md"], capture_output=True, text=True, check=True).stdout
out = [base.rstrip(), "", "## Measured by script (reference vs this render; sRGB 0-255, same procedure on both)", "", table.rstrip(), ""]
if prev:
    pair = [("current", root / f"renders/{v}.png"), ("earlier", root / f"renders/{prev}.png")]
    random.shuffle(pair)
    out += ["## Blind pairwise question (add to section 7 of your review)", "",
            "Two renders of the same subject follow, labelled X and Y. Say which is closer to the reference and why, in two sentences.",
            f"X: {pair[0][1]}", f"Y: {pair[1][1]}", ""]
    (root / "reviews" / f"pair_{v}.txt").write_text(f"X={pair[0][0]} Y={pair[1][0]}\n")
print("\n".join(out))
