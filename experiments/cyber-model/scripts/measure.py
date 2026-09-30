"""Measured table for this experiment: the reference vs a render, same procedure on both (tools/measure.py).
   python3 experiments/cyber-model/scripts/measure.py renders/v01.png [--md]
Kept as a wrapper so the frozen reviewer prompt's command still works."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parents[1] / "tools"))
from measure import table  # noqa: E402

if __name__ == "__main__":
    print(table(root / "references/ref_radio.jpg", sys.argv[1], "--md" in sys.argv))
