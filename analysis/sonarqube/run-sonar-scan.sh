#!/bin/bash
# Inventory analysis with SonarQube: scans the unmodified legacy POS code and
# publishes the results to the local dashboard (http://localhost:9000, project "legacy-pos").
#
# Needs: SonarQube running (./start-sonarqube.sh), JDK 17+, the scanner in
# ~/.sonar-scanner and an analysis token in ~/.sonarqube-pos-token (outside the repo).
# The legacy folder is not modified: classes and scanner work files go to a temp folder.
set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LEGACY="$ROOT/legacy-pos"
SCANNER="$(ls -d "$HOME"/.sonar-scanner/sonar-scanner-*/bin/sonar-scanner | head -1)"
TOKEN="$(cat "$HOME/.sonarqube-pos-token")"
WORK="$(mktemp -d)"
JUNIT="$HOME/.sonar-scanner/junit"

# JUnit is needed only to compile the legacy tests for analysis
mkdir -p "$JUNIT"
[ -f "$JUNIT/junit-4.12.jar" ] || curl -sL -o "$JUNIT/junit-4.12.jar" https://repo1.maven.org/maven2/junit/junit/4.12/junit-4.12.jar
[ -f "$JUNIT/hamcrest-core-1.3.jar" ] || curl -sL -o "$JUNIT/hamcrest-core-1.3.jar" https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar

echo "1/2 Compiling the legacy code (SonarQube's Java analyser reads source + bytecode)..."
cd "$LEGACY"
javac -encoding UTF-8 -nowarn -d "$WORK/classes" $(find src -name '*.java') 2>/dev/null
javac -encoding UTF-8 -nowarn -d "$WORK/test-classes" -cp "$WORK/classes:$JUNIT/junit-4.12.jar" $(find test -name '*.java') 2>/dev/null

echo "2/2 Running SonarScanner..."
"$SCANNER" \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token="$TOKEN" \
  -Dsonar.projectKey=legacy-pos \
  -Dsonar.projectName="Legacy POS (yangzai/unit1-ca)" \
  -Dsonar.projectBaseDir="$LEGACY" \
  -Dsonar.sources=src \
  -Dsonar.tests=test \
  -Dsonar.sourceEncoding=UTF-8 \
  -Dsonar.java.source=8 \
  -Dsonar.java.binaries="$WORK/classes" \
  -Dsonar.java.test.binaries="$WORK/test-classes" \
  -Dsonar.java.test.libraries="$JUNIT/junit-4.12.jar,$JUNIT/hamcrest-core-1.3.jar" \
  -Dsonar.working.directory="$WORK/scannerwork" \
  -Dsonar.qualitygate.wait=false \
  | grep -E "INFO: (ANALYSIS SUCCESSFUL|Analysis report uploaded|EXECUTION SUCCESS)|ANALYSIS SUCCESSFUL|EXECUTION SUCCESS|ERROR" || true

rm -rf "$WORK"
echo "Done. Dashboard: http://localhost:9000/dashboard?id=legacy-pos"
