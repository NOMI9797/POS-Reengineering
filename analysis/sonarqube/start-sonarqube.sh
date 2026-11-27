#!/bin/bash
# Starts the local SonarQube server (Docker) and waits until it is ready.
# Works with Docker Desktop or Colima. Dashboard: http://localhost:9000
set -e

if ! docker info >/dev/null 2>&1; then
  if command -v colima >/dev/null 2>&1; then
    echo "Starting Docker (Colima)..."
    colima start >/dev/null 2>&1
  else
    echo "Docker is not running. Start Docker Desktop (or Colima) and run this script again."
    exit 1
  fi
fi

# Elasticsearch inside SonarQube needs this kernel setting (only possible to set on Colima;
# Docker Desktop already allows it, and the bootstrap check is disabled below anyway)
if command -v colima >/dev/null 2>&1 && colima status >/dev/null 2>&1; then
  colima ssh -- sudo sysctl -w vm.max_map_count=524288 >/dev/null 2>&1 || true
fi

if docker ps -a --format '{{.Names}}' | grep -qx sonarqube; then
  docker start sonarqube >/dev/null
else
  echo "First start: downloading SonarQube (about 2.5 GB, once)..."
  docker run -d --name sonarqube -p 9000:9000 \
    -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
    -v sonarqube_data:/opt/sonarqube/data \
    -v sonarqube_extensions:/opt/sonarqube/extensions \
    -v sonarqube_logs:/opt/sonarqube/logs \
    sonarqube:community >/dev/null
fi

echo -n "Waiting for SonarQube"
for _ in $(seq 1 60); do
  if curl -s localhost:9000/api/system/status | grep -q '"status":"UP"'; then
    echo " - ready."
    echo "Open http://localhost:9000 in the browser."
    exit 0
  fi
  echo -n "."
  sleep 5
done
echo " - not ready after 5 minutes; check: docker logs sonarqube"
exit 1
