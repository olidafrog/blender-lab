#!/usr/bin/env bash
# Build the local Blender reference in reference/ (not in git). Safe to re-run.
#
#   tools/fetch_docs.sh            API docs for the installed Blender + manual + release notes
#   tools/fetch_docs.sh 4.4        also the API docs for another version
#
# Needs: curl, git, python3, unzip. Takes a few minutes; downloads ~100 MB per API version.
set -euo pipefail
cd "$(dirname "$0")/.."
REF=reference; TMP="$REF/.tmp"; mkdir -p "$REF" "$TMP"

# 1. Exact API of the installed Blender (seconds)
tools/blender.sh tools/dump_api.py

# 2. Python API docs (prose + examples), as text
ver_here="$(ls -td "$REF"/api-dump-* | head -1 | sed 's#.*api-dump-##')"
for v in $(printf '%s\n' "${ver_here:-}" "$@" | grep -E '^[0-9]+\.[0-9]+$' | sort -u); do
  u=${v/./_}
  if [[ ! -d "$REF/api-docs-$v" ]]; then
    echo "API docs $v"
    curl -sfL -o "$TMP/api-$v.zip" "https://docs.blender.org/api/$v/blender_python_reference_$u.zip"
    rm -rf "$TMP/api-$v"; unzip -q "$TMP/api-$v.zip" -d "$TMP/api-$v"
    python3 tools/html_to_text.py "$TMP/api-$v"/blender_python_reference_* "$REF/api-docs-$v"
    rm -rf "$TMP/api-$v" "$TMP/api-$v.zip"
  fi
done

# 3. User manual, text source only (reStructuredText, no images)
sparse_clone() {  # url dir pattern...
  local url=$1 dir=$2; shift 2
  if [[ -d "$dir/.git" ]]; then git -C "$dir" pull -q --depth 1; return; fi
  git clone -q --depth 1 --filter=blob:none --sparse "$url" "$dir"
  git -C "$dir" sparse-checkout set --no-cone "$@"
}
echo "Manual"
sparse_clone https://projects.blender.org/blender/blender-manual.git "$REF/manual" '/manual/**/*.rst'
echo "Release notes"
sparse_clone https://projects.blender.org/blender/blender-developer-docs.git "$REF/dev-docs" '/docs/release_notes/**/*.md'

rm -rf "$TMP"
du -sh "$REF"/* | sed 's#reference/##'
echo "fetch_docs OK"
