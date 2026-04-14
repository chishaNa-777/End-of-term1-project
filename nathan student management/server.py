#!/usr/bin/env python3
"""
Combined Server for Student Management System
Serves both the Flask API and static mobile app files
"""

import os
import sys
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import sqlite3
from werkzeug.security import check_password_hash

# Import the mobile API functions
try:
    from mobile_api import login, parent_dashboard, parent_grades, parent_payments, parent_attendance, parent_notifications, parent_messages, send_parent_message
    from student_managemnt import init_database
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure mobile_api.py and student_managemnt.py are in the same directory.")
    sys.exit(1)

# Create main app
app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

# Register API routes
@app.route('/api/login', methods=['POST'])
def api_login():
    return login()

@app.route('/api/parent/dashboard')
def api_dashboard():
    return parent_dashboard()

@app.route('/api/parent/grades/<student_id>')
def api_grades(student_id):
    return parent_grades(student_id)

@app.route('/api/parent/payments/<student_id>')
def api_payments(student_id):
    return parent_payments(student_id)

@app.route('/api/parent/attendance/<student_id>')
def api_attendance(student_id):
    return parent_attendance(student_id)

@app.route('/api/parent/notifications')
def api_notifications():
    return parent_notifications()

@app.route('/api/parent/messages')
def api_messages():
    return parent_messages()

@app.route('/api/parent/send-message', methods=['POST'])
def api_send_message():
    return send_parent_message()

# Serve mobile app files
@app.route('/')
def serve_mobile_app():
    return send_from_directory('.', 'mobile_app.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'services': {
            'api': 'running',
            'static_files': 'serving'
        }
    })

def main():
    # Initialize database
    print("Initializing database...")
    init_database()

    # Start server
    print("Starting combined server...")
    print("Mobile app: http://localhost:5000")
    print("API endpoints: http://localhost:5000/api/*")
    print("Press Ctrl+C to stop")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

if __name__ == '__main__':
    main()