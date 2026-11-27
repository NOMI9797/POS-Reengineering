#!/bin/bash
# Stops SonarQube and Docker to free memory. Results stay saved for the next start.
docker stop sonarqube >/dev/null 2>&1 && echo "SonarQube stopped."
colima stop >/dev/null 2>&1 && echo "Docker (Colima) stopped."
