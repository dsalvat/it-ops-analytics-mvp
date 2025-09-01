#!/bin/bash

# Start SonarQube container
docker run -d --name it-ops-sonarqube -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community

# Wait for SonarQube to be ready
echo "Waiting for SonarQube to start..."
while ! curl -s http://localhost:9000/api/system/status | grep -q '"status":"UP"'; do
  sleep 5
done
echo "SonarQube is up and running."

# Get a login token
echo "Please go to http://localhost:9000, log in (admin/admin), and generate a token."
read -p "Enter your SonarQube token: " SONAR_TOKEN

# Run Sonar Scanner for backend
docker run --rm --network=host -e SONAR_HOST_URL="http://localhost:9000" -e SONAR_LOGIN="$SONAR_TOKEN" -v "$(pwd)/backend:/usr/src" sonarsource/sonar-scanner-cli

# Run Sonar Scanner for frontend
docker run --rm --network=host -e SONAR_HOST_URL="http://localhost:9000" -e SONAR_LOGIN="$SONAR_TOKEN" -v "$(pwd)/frontend:/usr/src" sonarsource/sonar-scanner-cli

# Stop and remove SonarQube container
echo "Stopping and removing SonarQube container..."
docker stop it-ops-sonarqube
docker rm it-ops-sonarqube

echo "SonarQube analysis complete."
