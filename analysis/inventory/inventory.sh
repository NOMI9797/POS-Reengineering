#!/bin/bash
# Phase 1 – Inventory Analysis: regenerates every measured number in the
# inventory (docs/01, report section 2) from the unmodified legacy code.
#
# Tools: find, wc, grep (static analysis), javac + jdeps (JDK dependency
# analyser), git (history of the original repository).
# Usage: ./analysis/inventory/inventory.sh      (from the repository root; JDK 11+)
# Output: printed and saved to analysis/inventory/output/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LEGACY="$ROOT/legacy-pos"
SRC="$LEGACY/src/sg/edu/nus/iss/se24_2ft/unit1/ca"
OUT="$ROOT/analysis/inventory/output"
WORK="$(mktemp -d)"
mkdir -p "$OUT"
cd "$LEGACY"

section() { printf '\n== %s\n' "$1"; }

{
section "1. Asset counts"
echo "production .java files : $(find src -name '*.java' | wc -l | tr -d ' ')"
# Line counts use Python: 22 files lack a final newline (wc -l and some grep
# builds skip that line) and 11 files use Windows CRLF endings (awk NF miscounts).
python3 - <<'PYCOUNT'
import pathlib
def count(folder):
    files = list(pathlib.Path(folder).rglob('*.java'))
    lines = [f.read_bytes().decode('utf-8').splitlines() for f in files]
    total = sum(len(l) for l in lines)
    nonblank = sum(1 for l in lines for x in l if x.strip())
    no_eol = sum(1 for f in files if not f.read_bytes().endswith(b'\n'))
    crlf = sum(1 for f in files if b'\r\n' in f.read_bytes())
    return len(files), total, nonblank, no_eol, crlf
n, t, nb, ne, cr = count('src')
print(f"production lines       : {t} ({nb} non-blank); {ne} files lack a final newline, {cr} use CRLF line endings")
n, t, nb, ne, cr = count('test')
print(f"test lines             : {t}")
PYCOUNT
echo "packages               : $(find "$SRC" -type d | wc -l | tr -d ' ')"
echo "test .java files       : $(find test -name '*.java' | wc -l | tr -d ' ')"
echo "test methods (@Test)   : $(cat $(find test -name '*.java') | grep -c '@Test')"
echo "data files             : $(ls data-sample | wc -l | tr -d ' ')"
echo "config/build/tool files: $(ls -a | grep -cE '^\.(classpath|project|gitignore)$|\.iml$|\.eml$|\.userlibraries$') top-level IDE files, $(ls .idea | wc -l | tr -d ' ') in .idea, $(ls submission/*.bat submission.* tools/* | wc -l | tr -d ' ') scripts/tools"

section "2. Smell indicators"
echo "TODO comments          : $(grep -rn 'TODO' src | wc -l | tr -d ' ')"
echo "printStackTrace calls  : $(grep -rn 'printStackTrace' src | wc -l | tr -d ' ')"
echo "commented-out code     : $(grep -rnE '^\s*//\s*(public|private|[a-zA-Z_]+\s*[=(.]|return|if|\}|//)' src | wc -l | tr -d ' ') lines"
echo "non-GUI classes importing javax.swing:"
grep -rl 'javax.swing' src | grep -v '/gui/' | sed 's#.*/ca/#   #'

section "3. Lines of code per class (largest first)"
for f in $(find src -name '*.java'); do
  printf '%5d  %s\n' "$(python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read().splitlines()))' "$f")" "$(basename "$f" .java)"
done | sort -rn

section "4. Obsolete check: references to each class from OTHER files"
echo "(0 = never referenced anywhere else -> obsolete candidate)"
for f in $(find src -name '*.java'); do
  cls=$(basename "$f" .java)
  n=$( (grep -rlw "$cls" src || true) | (grep -v "/$cls.java$" || true) | wc -l | tr -d ' ')
  printf '%3d  %s\n' "$n" "$cls"
done | sort -n
echo "VendorManager: the variable created in StoreApplication is used $(grep -c 'vendorManager' "$SRC/StoreApplication.java") time(s) (only at creation)"

section "5. Data files (rows, trailing newline)"
for f in data-sample/*; do
  nl=$(tail -c1 "$f" | xxd -p)
  printf '%-18s rows=%-3s trailing-newline=%s\n' "$(basename "$f")" "$(grep -c . "$f")" "$([ "$nl" = "0a" ] && echo yes || echo no)"
done

section "6. Package dependencies (jdeps, JDK $(jdeps --version))"
javac -encoding UTF-8 -nowarn -d "$WORK/classes" $(find src -name '*.java') 2>/dev/null
jdeps -verbose:package "$WORK/classes" | sed 's/sg\.edu\.nus\.iss\.se24_2ft\.unit1\.ca/ca/g' > "$OUT/jdeps-packages.txt"
jdeps -verbose:package --dot-output "$OUT" "$WORK/classes" >/dev/null
echo "application package -> application package edges:"
grep -E '^\s+ca[a-z.]*\s+-> ca' "$OUT/jdeps-packages.txt" | awk '{print "   " $1 " -> " $3}' | sort -u
echo "edges: $(grep -E '^\s+ca[a-z.]*\s+-> ca' "$OUT/jdeps-packages.txt" | wc -l | tr -d ' ')"
echo "business packages depending on the GUI toolkit (javax.swing / java.awt):"
grep -E '^\s+ca\.(category|customer|discount|product|transaction|storekeeper|vendor|util|printer)[a-z.]*\s+-> (javax\.swing|java\.awt)' \
  "$OUT/jdeps-packages.txt" | awk '{print "   " $1 " -> " $3}' | sort -u
echo "full jdeps output: analysis/inventory/output/jdeps-packages.txt, DOT graph: analysis/inventory/output/classes.dot"

section "7. Original git history (github.com/yangzai/unit1-ca)"
if git clone --quiet https://github.com/yangzai/unit1-ca "$WORK/original" 2>/dev/null; then
  cd "$WORK/original"
  echo "commits      : $(git log --oneline | wc -l | tr -d ' ')"
  echo "first commit : $(git log --reverse --format=%ad --date=short | head -1)"
  echo "last commit  : $(git log -1 --format=%ad --date=short)"
  echo "author names : $(git log --format=%an | sort -u | wc -l | tr -d ' ')"
  echo "branches     : $(git branch -r | grep -v HEAD | wc -l | tr -d ' ') remote"
else
  echo "(offline: could not clone the original repository)"
fi
} 2>&1 | tee "$OUT/inventory-report.txt"

rm -rf "$WORK"
