# Parent Portal Setup and Demo Script
# This script demonstrates how to set up parent accounts and link them to students

import sqlite3
import os
import sys
import hashlib

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from student_managemnt import init_database, get_db_connection

def setup_parent_accounts():
    """Set up sample parent accounts and link them to students"""
    print("👨‍👩‍👧‍👦 Parent Portal Setup Demo")
    print("=" * 60)

    # Initialize database
    init_database()
    conn = get_db_connection()

    try:
        # Get real student IDs from database
        real_students = conn.execute("SELECT student_id, name FROM students LIMIT 3").fetchall()
        
        if len(real_students) < 3:
            print("❌ Not enough students in database. Please add some students first.")
            return None

        # Create sample parent users with real student IDs
        parents_data = [
            ('parent_john', 'john123', real_students[0][0], real_students[0][1]),
            ('parent_mary', 'mary123', real_students[1][0] if len(real_students) > 1 else real_students[0][0], real_students[1][1] if len(real_students) > 1 else real_students[0][1]),
            ('parent_david', 'david123', real_students[2][0] if len(real_students) > 2 else real_students[0][0], real_students[2][1] if len(real_students) > 2 else real_students[0][1]),
        ]

        print("\n1. Creating Parent Accounts:")

        # Delete existing parent accounts to recreate with proper hashing
        conn.execute("DELETE FROM users WHERE role = 'parent'")
        conn.execute("DELETE FROM parent_students")
        print("   🗑️  Cleared existing parent accounts")

        for username, password, student_id, student_name in parents_data:
            # Hash password using SHA256 (deterministic)
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()

            # Check if user already exists
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                print(f"   ⚠️  Parent account '{username}' already exists - skipping")
                continue

            # Create parent user
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, role, created_at)
                VALUES (?, ?, 'parent', CURRENT_TIMESTAMP)
            ''', (username, hashed_pass))

            parent_id = cursor.lastrowid
            print(f"   ✅ Created parent account: {username} (ID: {parent_id})")

            # Link parent to student
            cursor.execute('''
                INSERT INTO parent_students (parent_user_id, student_id, relationship, is_primary,
                                           can_view_grades, can_view_payments, can_view_attendance)
                VALUES (?, ?, 'Parent', 1, 1, 1, 1)
            ''', (parent_id, student_id))

            print(f"   ✅ Linked {username} to student {student_id}")

        conn.commit()

        # Show current parent accounts
        print("\n2. Current Parent Accounts:")
        parents = conn.execute('''
            SELECT u.username, u.role, ps.student_id, s.name as student_name
            FROM users u
            JOIN parent_students ps ON u.id = ps.parent_user_id
            JOIN students s ON ps.student_id = s.student_id
            WHERE u.role = 'parent'
            ORDER BY u.username
        ''').fetchall()

        for parent in parents:
            print(f"   • {parent['username']} -> {parent['student_name']} ({parent['student_id']})")

        # Show parent portal features
        print("\n3. Parent Portal Features:")
        print("   ✅ Dashboard with children overview")
        print("   ✅ Academic progress tracking")
        print("   ✅ Payment status monitoring")
        print("   ✅ Attendance records")
        print("   ✅ Report card access")
        print("   ✅ Notification system")
        print("   ✅ Messaging with administrators")
        print("   ✅ Account settings")

        print("\n4. How Parents Can Use the System:")
        print("   📝 Login with their parent account credentials")
        print("   👀 View their children's academic performance")
        print("   💰 Monitor payment status and due dates")
        print("   📅 Check attendance records")
        print("   📄 Access report cards and transcripts")
        print("   🔔 Receive important notifications")
        print("   💬 Communicate with school administrators")
        print("   ⚙️ Manage their account preferences")

        print("\n5. Sample Login Credentials:")
        for username, password, _, _ in parents_data:
            print(f"   Username: {username} | Password: {password}")

        print("\n" + "=" * 60)
        print("🎉 Parent Portal Setup Complete!")
        print("\n🚀 Parents can now login to the system using the credentials above.")
        print("   The application will automatically show the parent-specific interface.")
        print("   Run 'python student_managemnt.py' and login with parent credentials to explore!")

    finally:
        conn.close()

def demonstrate_parent_features(conn=None):
    """Demonstrate parent portal features with sample data"""
    print("\n🔍 Demonstrating Parent Portal Features:")
    print("-" * 50)

    if conn is None:
        conn = get_db_connection()

    try:
        # Get a sample parent
        parent = conn.execute('''
            SELECT u.id, u.username, ps.student_id, s.name as student_name
            FROM users u
            JOIN parent_students ps ON u.id = ps.parent_user_id
            JOIN students s ON ps.student_id = s.student_id
            WHERE u.role = 'parent'
            LIMIT 1
        ''').fetchone()

        if not parent:
            print("❌ No parent accounts found. Run setup_parent_accounts() first.")
            return

        print(f"📋 Sample Parent: {parent['username']}")
        print(f"👨‍🎓 Linked Student: {parent['student_name']} ({parent['student_id']})")

        # Show what the parent would see
        print("\n👀 Parent Dashboard Overview:")

        # Academic summary
        grades = conn.execute('''
            SELECT subject_name, marks, semester
            FROM subjects
            WHERE student_id = ?
            ORDER BY marks DESC
            LIMIT 3
        ''', (parent['student_id'],)).fetchall()

        if grades:
            print("   📚 Top Grades:")
            for grade in grades:
                print(".1f")

        # Payment summary
        payments = conn.execute('''
            SELECT pc.name, p.amount, p.status, p.due_date
            FROM payments p
            JOIN payment_categories pc ON p.category_id = pc.id
            WHERE p.student_id = ?
            ORDER BY p.due_date DESC
            LIMIT 3
        ''', (parent['student_id'],)).fetchall()

        if payments:
            print("   💰 Recent Payments:")
            for payment in payments:
                print(f"      • {payment['name']}: ${payment['amount']:.2f} ({payment['status']})")

        # Attendance summary
        attendance = conn.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
            FROM attendance
            WHERE student_id = ?
        ''', (parent['student_id'],)).fetchone()

        if attendance['total'] > 0:
            rate = (attendance['present'] / attendance['total']) * 100
            print(".1f")

        # Notifications for parent
        notifications = conn.execute('''
            SELECT title, type, created_at
            FROM notifications
            WHERE recipient_type = 'all' OR recipient_id = ?
            ORDER BY created_at DESC
            LIMIT 3
        ''', (parent['username'],)).fetchall()

        if notifications:
            print("   🔔 Recent Notifications:")
            for notif in notifications:
                print(f"      • {notif['title']} ({notif['type']})")

        print("\n✨ Parent Portal Benefits:")
        print("   • Real-time access to child's academic progress")
        print("   • Transparent payment tracking and reminders")
        print("   • Immediate notification of important updates")
        print("   • Direct communication channel with school")
        print("   • Secure access to sensitive student information")
        print("   • Mobile-friendly interface for on-the-go access")

    except Exception as e:
        print(f"Error setting up parent accounts: {str(e)}")
        return None
    
    return conn

if __name__ == "__main__":
    conn = setup_parent_accounts()
    demonstrate_parent_features(conn)
    conn.close()