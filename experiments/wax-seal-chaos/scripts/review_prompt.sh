#!/bin/sh
# Print the reviewer prompt for one version: REVIEWER_PROMPT.md + composite paths. Usage: review_prompt.sh v01
E=$(cd "$(dirname "$0")/.." && pwd)
cat "$E/reviews/REVIEWER_PROMPT.md"
echo; echo "Render: $E/renders/$1.png"; echo "Side-by-side composites:"
for f in "$E/reviews/sbs_$1"/*.png; do echo "- $f"; done
echo "References:"; for f in "$E/references"/*; do echo "- $f"; done
echo; echo "Write your review to \`$E/reviews/review_$1.md\`."
