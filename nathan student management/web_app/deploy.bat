@echo off
REM Student Management System - Docker Deployment Script (Windows)
REM This script helps deploy the application using Docker Compose

echo 🚀 Student Management System - Docker Deployment
echo =================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

REM Navigate to docker directory
cd /d "%~dp0docker"

echo 📦 Building and starting services...
docker-compose up --build -d

if %errorlevel% neq 0 (
    REM Try with newer Docker Compose syntax
    docker compose up --build -d
)

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps
if %errorlevel% neq 0 (
    docker compose ps
)

echo.
echo ✅ Deployment completed!
echo 🌐 Frontend: http://localhost
echo 🔗 API: http://localhost/api
echo.
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo 🧹 To clean up: docker-compose down -v
echo.
pause