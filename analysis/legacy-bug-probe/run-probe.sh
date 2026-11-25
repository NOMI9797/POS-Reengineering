#!/bin/bash
# Re-runs the legacy defect probes (P1-P8) against the untouched legacy code.
# Usage: ./run-probe.sh   (needs JDK 11+, curl; run from this folder)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
LEGACY="$HERE/../../legacy-pos"
WORK="$(mktemp -d)"
javac -encoding UTF-8 -d "$WORK/legacy" $(find "$LEGACY/src" -name '*.java')
javac -encoding UTF-8 -d "$WORK/probe" -cp "$WORK/legacy" "$HERE/Probe.java"
java -Dsample="$LEGACY/data-sample" -cp "$WORK/legacy:$WORK/probe" Probe 2>&1 | grep -v '^\s*at '
