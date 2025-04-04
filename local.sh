#!/bin/bash

# [1] Based on standard Docker Compose practice, this script was assembled with ChatGPT's guidance for automation of build and run.
# Build and run the Docker container
echo "Building Docker image..."
docker-compose build

echo "Starting Docker container..."
docker-compose up -d

echo "PAS service is running at http://localhost:8080/"
echo "To stop the service, run: docker-compose down"
