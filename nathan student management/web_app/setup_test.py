#!/usr/bin/env python3
"""
Student Management System - Quick Setup Test
This script performs basic validation of the web application setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def run_command(cmd, description):
    """Run a command and check if it succeeds."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}: Success")
            return True
        else:
            print(f"❌ {description}: Failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)}")
        return False

def main():
    print("🧪 Student Management System - Setup Validation")
    print("=" * 55)

    base_dir = Path(__file__).parent
    all_checks_passed = True

    # Check directory structure
    print("\n📁 Checking directory structure...")
    dirs_to_check = [
        ("backend", "Backend directory"),
        ("backend/app", "Backend app directory"),
        ("backend/app/routes", "Backend routes directory"),
        ("frontend", "Frontend directory"),
        ("frontend/src", "Frontend src directory"),
        ("docker", "Docker directory"),
    ]

    for dir_path, description in dirs_to_check:
        if not check_directory_exists(base_dir / dir_path, description):
            all_checks_passed = False

    # Check key files
    print("\n📄 Checking key files...")
    files_to_check = [
        ("backend/requirements.txt", "Backend requirements.txt"),
        ("backend/run.py", "Backend run.py"),
        ("backend/app/__init__.py", "Backend app factory"),
        ("backend/app/models.py", "Backend models.py"),
        ("frontend/package.json", "Frontend package.json"),
        ("frontend/src/App.js", "Frontend App.js"),
        ("docker/docker-compose.yml", "Docker Compose config"),
        ("docker/Dockerfile.backend", "Backend Dockerfile"),
        ("docker/Dockerfile.frontend", "Frontend Dockerfile"),
        ("docker/nginx.conf", "Nginx configuration"),
    ]

    for file_path, description in files_to_check:
        if not check_file_exists(base_dir / file_path, description):
            all_checks_passed = False

    # Check Python environment (if available)
    print("\n🐍 Checking Python environment...")
    if run_command("python --version", "Python availability"):
        # Check if required packages can be imported
        try:
            import flask
            print("✅ Flask: Available")
        except ImportError:
            print("⚠️  Flask: Not installed (will be installed in Docker)")

        try:
            import flask_jwt_extended
            print("✅ Flask-JWT-Extended: Available")
        except ImportError:
            print("⚠️  Flask-JWT-Extended: Not installed (will be installed in Docker)")

    # Check Node.js environment (if available)
    print("\n📦 Checking Node.js environment...")
    if run_command("node --version", "Node.js availability"):
        if run_command("npm --version", "npm availability"):
            # Check if React dependencies are available
            package_json = base_dir / "frontend" / "package.json"
            if package_json.exists():
                print("✅ Frontend dependencies: Configured")

    # Check Docker environment
    print("\n🐳 Checking Docker environment...")
    docker_available = run_command("docker --version", "Docker availability")
    if docker_available:
        compose_available = run_command("docker-compose --version", "Docker Compose availability")
        if not compose_available:
            # Try newer syntax
            run_command("docker compose version", "Docker Compose (new syntax)")

    print("\n" + "=" * 55)
    if all_checks_passed:
        print("🎉 Setup validation completed successfully!")
        print("\n🚀 Ready to deploy! Run one of these commands:")
        print("   Linux/Mac: ./deploy.sh")
        print("   Windows: deploy.bat")
        print("   Manual: cd docker && docker-compose up --build")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("   You can still attempt deployment, but some features may not work.")

    print("\n🌐 After deployment, access at: http://localhost")
    print("🔗 API documentation at: http://localhost/api")
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())