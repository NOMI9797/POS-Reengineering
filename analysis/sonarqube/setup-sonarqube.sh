#!/bin/bash
# One-time SonarQube setup on YOUR OWN laptop. Each team member runs this once.
#
# What it does:
#   1. checks Java 17+, Docker and free disk space
#   2. starts SonarQube in Docker (downloads it the first time, about 2.5 GB)
#   3. replaces the default admin/admin password with your own
#   4. creates an analysis token, saved in ~/.sonarqube-pos-token (outside the repository)
#   5. downloads SonarScanner (about 10 MB) into ~/.sonar-scanner
#   6. creates the "POS Inventory" quality profile (Sonar way + maintainability rules)
#      and makes it the default for Java
# Afterwards run: ./analysis/sonarqube/run-sonar-scan.sh
#
# Your password is asked for interactively (or taken from SONAR_ADMIN_PASSWORD).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
H=http://localhost:9000

echo "== 1/6 Checking requirements"
JV=$(java -version 2>&1 | sed -n 's/.*version "\([0-9]*\).*/\1/p' | head -1)
[ -n "$JV" ] && [ "$JV" -ge 17 ] || { echo "Java 17 or newer is required (found: ${JV:-none})."; exit 1; }
command -v docker >/dev/null || { echo "Docker is required: install Docker Desktop, or 'brew install colima docker'."; exit 1; }
FREE_GB=$(df -Pk "$HOME" | awk 'NR==2{print int($4/1048576)}')   # portable: macOS, Linux, WSL
if [ "${FREE_GB:-0}" -lt 5 ] && ! docker images -q sonarqube:community | grep -q .; then
  echo "Only ${FREE_GB} GB free. SonarQube needs about 4-5 GB on first download. Free some space first."
  exit 1
fi
echo "Java $JV, Docker found, ${FREE_GB} GB free."

echo "== 2/6 Starting SonarQube"
"$HERE/start-sonarqube.sh"

echo "== 3/6 Admin password"
PW="${SONAR_ADMIN_PASSWORD:-}"
if [ -z "$PW" ]; then
  echo "Choose a password for the SonarQube 'admin' user"
  echo "(12+ characters with upper case, lower case, a digit and a symbol, e.g. MyPos-Scan2026!)."
  read -r -s -p "Password: " PW; echo
fi
code=$(curl -s -o /dev/null -w '%{http_code}' -u admin:admin -X POST "$H/api/users/change_password" \
  --data-urlencode login=admin --data-urlencode previousPassword=admin --data-urlencode "password=$PW")
if [ "$code" = "204" ]; then
  echo "Password changed from the default."
elif curl -s -u "admin:$PW" "$H/api/authentication/validate" | grep -q '"valid":true'; then
  echo "Password was already set earlier; using it."
else
  echo "Could not set or use that password (HTTP $code). It must meet the rules above."
  exit 1
fi
AUTH="admin:$PW"

echo "== 4/6 Analysis token"
curl -s -o /dev/null -u "$AUTH" -X POST "$H/api/user_tokens/revoke" --data-urlencode name=pos-scan
curl -s -u "$AUTH" -X POST "$H/api/user_tokens/generate" \
  --data-urlencode name=pos-scan --data-urlencode type=GLOBAL_ANALYSIS_TOKEN \
  | sed -n 's/.*"token":"\([^"]*\)".*/\1/p' > "$HOME/.sonarqube-pos-token"
chmod 600 "$HOME/.sonarqube-pos-token"
[ -s "$HOME/.sonarqube-pos-token" ] || { echo "Token could not be created."; exit 1; }
echo "Token saved in ~/.sonarqube-pos-token"

echo "== 5/6 SonarScanner"
if ls -d "$HOME"/.sonar-scanner/sonar-scanner-*/bin/sonar-scanner >/dev/null 2>&1; then
  echo "Already installed."
else
  V=$(curl -s https://repo1.maven.org/maven2/org/sonarsource/scanner/cli/sonar-scanner-cli/maven-metadata.xml \
      | sed -n 's:.*<release>\(.*\)</release>.*:\1:p')
  mkdir -p "$HOME/.sonar-scanner"
  curl -sL -o "$HOME/.sonar-scanner/scanner.zip" \
    "https://repo1.maven.org/maven2/org/sonarsource/scanner/cli/sonar-scanner-cli/$V/sonar-scanner-cli-$V.zip"
  (cd "$HOME/.sonar-scanner" && unzip -qo scanner.zip && rm scanner.zip)
  echo "SonarScanner $V installed."
fi

echo "== 6/6 Quality profile 'POS Inventory'"
KEY=$(curl -s -u "$AUTH" "$H/api/qualityprofiles/search?language=java" | python3 -c '
import sys, json
p = [x for x in json.load(sys.stdin)["profiles"] if x["name"] == "POS Inventory"]
print(p[0]["key"] if p else "")')
if [ -z "$KEY" ]; then
  BASE=$(curl -s -u "$AUTH" "$H/api/qualityprofiles/search?language=java" | python3 -c '
import sys, json
print([x for x in json.load(sys.stdin)["profiles"] if x.get("isBuiltIn") and x["name"] == "Sonar way"][0]["key"])')
  KEY=$(curl -s -u "$AUTH" -X POST "$H/api/qualityprofiles/copy" --data-urlencode "fromKey=$BASE" \
        --data-urlencode "toName=POS Inventory" | python3 -c 'import sys, json; print(json.load(sys.stdin)["key"])')
fi
# TODO comments, commented-out code, unused code, long/complex methods, coupling, exception handling ...
for r in S1135 S125 S1128 S1144 S1068 S1481 S138 S1448 S1200 S3776 S1192 S108 S106 S1166 S2093 S1450 \
         S1172 S1186 S2209 S1604 S1854 S3008 S2696 S1659; do
  curl -s -o /dev/null -u "$AUTH" -X POST "$H/api/qualityprofiles/activate_rule" \
    --data-urlencode "key=$KEY" --data-urlencode "rule=java:$r"
done
curl -s -o /dev/null -u "$AUTH" -X POST "$H/api/qualityprofiles/set_default" \
  --data-urlencode language=java --data-urlencode "qualityProfile=POS Inventory"
echo "Profile ready and set as default."

echo
echo "Setup complete. Next: ./analysis/sonarqube/run-sonar-scan.sh"
echo "Dashboard: $H  (login: admin / the password you chose)"
