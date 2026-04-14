# Mobile App API for Student Management System
# This creates a REST API that mobile apps can connect to

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import jwt
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
CORS(app)  # Enable CORS for mobile app access

DB_FILE = "student_db.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, role):
    """Generate JWT token for mobile authentication"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require authentication token"""
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        # Add user info to request
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.route('/api/login', methods=['POST'])
def login():
    """Mobile app login endpoint"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    username = data['username']
    password = hash_password(data['password'])

    conn = get_db_connection()
    try:
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                          (username, password)).fetchone()

        if user:
            token = generate_token(user['id'], user['role'])

            # Update last login
            conn.execute("UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now(), user['id']))
            conn.commit()

            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    finally:
        conn.close()

@app.route('/api/logout', methods=['POST'])
@token_required
def logout():
    """Mobile app logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    return jsonify({'message': 'Logged out successfully'})

# ==========================================
# PARENT PORTAL ENDPOINTS
# ==========================================

@app.route('/api/parent/dashboard', methods=['GET'])
@token_required
def parent_dashboard():
    """Get parent dashboard data"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    try:
        # Get children
        children = conn.execute('''
            SELECT s.student_id, s.name, s.program, s.enrollment_date
            FROM parent_students ps
            JOIN students s ON ps.student_id = s.student_id
            WHERE ps.parent_user_id = ?
        ''', (request.user_id,)).fetchall()

        dashboard_data = []
        for child in children:
            # Get GPA
            gpa_result = conn.execute('''
                SELECT AVG(marks) as gpa FROM subjects WHERE student_id = ?
            ''', (child['student_id'],)).fetchone()
            gpa = round(gpa_result['gpa'], 2) if gpa_result['gpa'] else 0

            # Get attendance rate
            attendance_result = conn.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
                FROM attendance WHERE student_id = ?
            ''', (child['student_id'],)).fetchone()
            attendance_rate = (attendance_result['present'] / attendance_result['total'] * 100) if attendance_result['total'] > 0 else 0

            # Get payment status
            payment_result = conn.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END) as paid
                FROM payments WHERE student_id = ?
            ''', (child['student_id'],)).fetchone()
            payment_completion = (payment_result['paid'] / payment_result['total'] * 100) if payment_result['total'] > 0 else 100

            dashboard_data.append({
                'student_id': child['student_id'],
                'name': child['name'],
                'program': child['program'],
                'gpa': gpa,
                'attendance_rate': round(attendance_rate, 1),
                'payment_completion': round(payment_completion, 1)
            })

        return jsonify({'children': dashboard_data})

    finally:
        conn.close()

@app.route('/api/parent/grades/<student_id>', methods=['GET'])
@token_required
def parent_grades(student_id):
    """Get grades for a specific child"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    # Verify parent has access to this student
    conn = get_db_connection()
    try:
        access_check = conn.execute('''
            SELECT 1 FROM parent_students
            WHERE parent_user_id = ? AND student_id = ?
        ''', (request.user_id, student_id)).fetchone()

        if not access_check:
            return jsonify({'error': 'Access denied to this student'}), 403

        # Get grades
        grades = conn.execute('''
            SELECT subject_name, marks, credits, semester
            FROM subjects
            WHERE student_id = ?
            ORDER BY semester DESC, subject_name
        ''', (student_id,)).fetchall()

        # Calculate GPA
        if grades:
            total_points = sum(grade['marks'] * grade['credits'] for grade in grades)
            total_credits = sum(grade['credits'] for grade in grades)
            gpa = total_points / total_credits if total_credits > 0 else 0
        else:
            gpa = 0

        grades_list = [{
            'subject': grade['subject_name'],
            'marks': grade['marks'],
            'credits': grade['credits'],
            'semester': grade['semester'],
            'grade': calculate_grade_letter(grade['marks'])
        } for grade in grades]

        return jsonify({
            'student_id': student_id,
            'gpa': round(gpa, 2),
            'grades': grades_list
        })

    finally:
        conn.close()

def calculate_grade_letter(marks):
    """Convert marks to grade letter"""
    if marks >= 90: return 'A+'
    elif marks >= 85: return 'A'
    elif marks >= 80: return 'A-'
    elif marks >= 75: return 'B+'
    elif marks >= 70: return 'B'
    elif marks >= 65: return 'B-'
    elif marks >= 60: return 'C+'
    elif marks >= 55: return 'C'
    elif marks >= 50: return 'C-'
    elif marks >= 45: return 'D'
    else: return 'F'

@app.route('/api/parent/payments/<student_id>', methods=['GET'])
@token_required
def parent_payments(student_id):
    """Get payment information for a specific child"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    # Verify parent has access to this student
    conn = get_db_connection()
    try:
        access_check = conn.execute('''
            SELECT 1 FROM parent_students
            WHERE parent_user_id = ? AND student_id = ?
        ''', (request.user_id, student_id)).fetchone()

        if not access_check:
            return jsonify({'error': 'Access denied to this student'}), 403

        # Get payments
        payments = conn.execute('''
            SELECT p.id, pc.name as category, p.amount, p.payment_date,
                   p.due_date, p.payment_method, p.status, p.notes
            FROM payments p
            JOIN payment_categories pc ON p.category_id = pc.id
            WHERE p.student_id = ?
            ORDER BY p.due_date DESC
        ''', (student_id,)).fetchall()

        # Calculate totals
        total_due = sum(p['amount'] for p in payments if p['status'] != 'Paid')
        total_paid = sum(p['amount'] for p in payments if p['status'] == 'Paid')

        payments_list = [{
            'id': payment['id'],
            'category': payment['category'],
            'amount': payment['amount'],
            'payment_date': payment['payment_date'],
            'due_date': payment['due_date'],
            'payment_method': payment['payment_method'],
            'status': payment['status'],
            'notes': payment['notes']
        } for payment in payments]

        return jsonify({
            'student_id': student_id,
            'total_paid': total_paid,
            'total_due': total_due,
            'payments': payments_list
        })

    finally:
        conn.close()

@app.route('/api/parent/attendance/<student_id>', methods=['GET'])
@token_required
def parent_attendance(student_id):
    """Get attendance information for a specific child"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    # Verify parent has access to this student
    conn = get_db_connection()
    try:
        access_check = conn.execute('''
            SELECT 1 FROM parent_students
            WHERE parent_user_id = ? AND student_id = ?
        ''', (request.user_id, student_id)).fetchone()

        if not access_check:
            return jsonify({'error': 'Access denied to this student'}), 403

        # Get attendance records (last 30 days)
        attendance = conn.execute('''
            SELECT date, status, remarks
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
            LIMIT 30
        ''', (student_id,)).fetchall()

        # Calculate attendance rate
        total_days = len(attendance)
        present_days = sum(1 for a in attendance if a['status'] == 'Present')
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

        attendance_list = [{
            'date': record['date'],
            'status': record['status'],
            'remarks': record['remarks']
        } for record in attendance]

        return jsonify({
            'student_id': student_id,
            'attendance_rate': round(attendance_rate, 1),
            'total_days': total_days,
            'present_days': present_days,
            'records': attendance_list
        })

    finally:
        conn.close()

@app.route('/api/parent/notifications', methods=['GET'])
@token_required
def parent_notifications():
    """Get notifications for parent"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    try:
        # Get unread count
        unread_count = conn.execute('''
            SELECT COUNT(*) FROM notification_recipients nr
            JOIN notifications n ON nr.notification_id = n.id
            WHERE nr.recipient_id = ? AND nr.is_read = 0 AND n.is_active = 1
        ''', (request.user_id,)).fetchone()[0]

        # Get recent notifications
        notifications = conn.execute('''
            SELECT n.id, n.title, n.message, n.type, n.priority, n.created_at,
                   nr.is_read, nr.read_at
            FROM notifications n
            LEFT JOIN notification_recipients nr ON n.id = nr.notification_id
                AND nr.recipient_id = ?
            WHERE n.recipient_type = 'all' OR nr.recipient_id = ?
            ORDER BY n.created_at DESC
            LIMIT 20
        ''', (request.user_id, request.user_id)).fetchall()

        notifications_list = [{
            'id': notif['id'],
            'title': notif['title'],
            'message': notif['message'],
            'type': notif['type'],
            'priority': notif['priority'],
            'created_at': notif['created_at'],
            'is_read': bool(notif['is_read']),
            'read_at': notif['read_at']
        } for notif in notifications]

        return jsonify({
            'unread_count': unread_count,
            'notifications': notifications_list
        })

    finally:
        conn.close()

@app.route('/api/parent/messages', methods=['GET'])
@token_required
def parent_messages():
    """Get messages for parent"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    try:
        messages = conn.execute('''
            SELECT pm.id, pm.subject, u.username as from_user, pm.message_type,
                   pm.status, pm.created_at, pm.admin_response, pm.admin_response_at
            FROM parent_messages pm
            LEFT JOIN users u ON pm.from_user_id = u.id
            WHERE pm.from_user_id = ? OR pm.to_user_id = ?
            ORDER BY pm.created_at DESC
        ''', (request.user_id, request.user_id)).fetchall()

        messages_list = [{
            'id': msg['id'],
            'subject': msg['subject'],
            'from_user': msg['from_user'] if msg['from_user'] else 'Admin',
            'message_type': msg['message_type'],
            'status': msg['status'],
            'created_at': msg['created_at'],
            'admin_response': msg['admin_response'],
            'admin_response_at': msg['admin_response_at']
        } for msg in messages]

        return jsonify({'messages': messages_list})

    finally:
        conn.close()

@app.route('/api/parent/send-message', methods=['POST'])
@token_required
def send_parent_message():
    """Send a message from parent to admin"""
    if request.user_role != 'parent':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data or not data.get('subject') or not data.get('message'):
        return jsonify({'error': 'Subject and message are required'}), 400

    conn = get_db_connection()
    try:
        # Find admin user
        admin = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
        if not admin:
            return jsonify({'error': 'No administrator found'}), 500

        conn.execute('''
            INSERT INTO parent_messages (from_user_id, to_user_id, subject, message,
                                       message_type, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (request.user_id, admin['id'], data['subject'], data['message'],
              data.get('message_type', 'general'), data.get('priority', 'normal')))

        conn.commit()
        return jsonify({'message': 'Message sent successfully'})

    finally:
        conn.close()

# ==========================================
# STUDENT ENDPOINTS (for future student mobile app)
# ==========================================

@app.route('/api/student/dashboard', methods=['GET'])
@token_required
def student_dashboard():
    """Get student dashboard data"""
    if request.user_role not in ['admin', 'user']:  # Assuming 'user' role for students
        return jsonify({'error': 'Access denied'}), 403

    # This would be implemented for student mobile access
    return jsonify({'message': 'Student dashboard - to be implemented'})

# ==========================================
# ADMIN ENDPOINTS
# ==========================================

@app.route('/api/admin/stats', methods=['GET'])
@token_required
def admin_stats():
    """Get system statistics for admin dashboard"""
    if request.user_role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    try:
        # Basic stats
        total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        total_payments = conn.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
        total_paid = conn.execute('SELECT SUM(amount) FROM payments WHERE status = "Paid"').fetchone()[0] or 0
        total_notifications = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_active = 1').fetchone()[0]

        return jsonify({
            'total_students': total_students,
            'total_payments': total_payments,
            'total_paid': total_paid,
            'total_notifications': total_notifications
        })

    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Starting Student Management Mobile API Server...")
    print("📱 API will be available at: http://localhost:5000")
    print("📚 Parent endpoints:")
    print("   POST /api/login - Login")
    print("   GET /api/parent/dashboard - Parent dashboard")
    print("   GET /api/parent/grades/<student_id> - Student grades")
    print("   GET /api/parent/payments/<student_id> - Payment info")
    print("   GET /api/parent/attendance/<student_id> - Attendance records")
    print("   GET /api/parent/notifications - Notifications")
    print("   GET /api/parent/messages - Messages")
    print("   POST /api/parent/send-message - Send message")
    app.run(debug=True, host='0.0.0.0', port=5000)