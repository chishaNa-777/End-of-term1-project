#!/bin/bash

# Student Management System - Docker Deployment Script
# This script helps deploy the application using Docker Compose

set -e

echo "🚀 Student Management System - Docker Deployment"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Navigate to docker directory
cd "$(dirname "$0")/docker"

echo "📦 Building and starting services..."
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

echo ""
echo "✅ Deployment completed!"
echo "🌐 Frontend: http://localhost"
echo "🔗 API: http://localhost/api"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🧹 To clean up: docker-compose down -v"