# Notification System Demo
# This script demonstrates how to use the notification system programmatically.

import sqlite3
import datetime

DB_FILE = "student_db.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def demo_notifications():
    """Demonstrate notification system functionality"""
    print("🔔 Notification System Demo")
    print("=" * 50)

    conn = get_db_connection()
    c = conn.cursor()

    # 1. Show notification types and settings
    print("\n📋 Notification Types:")
    notification_types = [
        ("payment_reminder", "Payment due date reminders"),
        ("payment_overdue", "Overdue payment notifications"),
        ("grade_posted", "New grade posted notifications"),
        ("gpa_update", "GPA calculation updates"),
        ("attendance_warning", "Low attendance warnings"),
        ("system_announcement", "System announcements and updates"),
        ("report_card_ready", "Report card generation notifications")
    ]

    for notif_type, description in notification_types:
        print(f"  • {notif_type}: {description}")

    # 2. Create sample notifications
    print("\n📤 Creating Sample Notifications:")

    # System announcement
    notif_id1 = create_notification(
        "Welcome to the New Academic Year!",
        "Dear Students and Staff,\n\nWelcome to the new academic year! We hope you had a great break and are ready for an exciting year ahead.\n\nPlease check your schedules and ensure all payments are up to date.\n\nBest regards,\nSchool Administration",
        "announcement",
        "normal",
        "all",
        None,
        "admin",
        30
    )
    print(f"  ✓ Created system announcement (ID: {notif_id1})")

    # Get a sample student
    student = c.execute("SELECT student_id, name FROM students LIMIT 1").fetchone()
    if student:
        student_id, student_name = student

        # Payment reminder
        notif_id2 = create_notification(
            "Tuition Fee Payment Reminder",
            f"Dear {student_name},\n\nThis is a reminder that your tuition fee payment is due in 3 days.\n\nAmount Due: $2,500.00\nDue Date: 2026-04-10\n\nPlease make your payment to avoid late fees.\n\nThank you!",
            "payment",
            "high",
            "specific_student",
            student_id,
            "system",
            7
        )
        print(f"  ✓ Created payment reminder for {student_name} (ID: {notif_id2})")

        # Grade notification
        notif_id3 = create_notification(
            "New Grade Posted: Mathematics - Final Exam",
            f"Dear {student_name},\n\nA new grade has been posted for Mathematics.\n\nAssessment: Final Exam\nGrade: A-\nScore: 88%\n\nPlease check your gradebook for detailed information.\n\nBest regards,\nAcademic Office",
            "grade",
            "normal",
            "specific_student",
            student_id,
            "system",
            30
        )
        print(f"  ✓ Created grade notification for {student_name} (ID: {notif_id3})")

    # 3. Show notification statistics
    print("\n📊 Notification Statistics:")
    stats = c.execute("""
        SELECT
            COUNT(*) as total_notifications,
            COUNT(CASE WHEN type = 'payment' THEN 1 END) as payment_notifications,
            COUNT(CASE WHEN type = 'grade' THEN 1 END) as grade_notifications,
            COUNT(CASE WHEN type = 'announcement' THEN 1 END) as announcements,
            COUNT(CASE WHEN priority = 'urgent' THEN 1 END) as urgent_notifications
        FROM notifications
        WHERE is_active = 1
    """).fetchall()

    if stats:
        stat = stats[0]
        print(f"  • Total Notifications: {stat[0]}")
        print(f"  • Payment Notifications: {stat[1]}")
        print(f"  • Grade Notifications: {stat[2]}")
        print(f"  • Announcements: {stat[3]}")
        print(f"  • Urgent Notifications: {stat[4]}")

    # 4. Show recent notifications
    print("\n🕒 Recent Notifications:")
    notifications = c.execute("""
        SELECT id, title, type, priority, recipient_type, created_at
        FROM notifications
        WHERE is_active = 1
        ORDER BY created_at DESC LIMIT 5
    """).fetchall()

    for notif in notifications:
        recipient_info = "All" if notif[4] == "all" else f"Student: {notif[4]}"
        print(f"  • [{notif[2].upper()}] {notif[1]}")
        print(f"    Priority: {notif[3]} | Recipients: {recipient_info} | Created: {notif[5]}")

    # 5. Show notification recipients
    print("\n👥 Notification Recipients:")
    recipients = c.execute("""
        SELECT n.title, COUNT(nr.id) as recipient_count, n.recipient_type
        FROM notifications n
        LEFT JOIN notification_recipients nr ON n.id = nr.notification_id
        WHERE n.is_active = 1
        GROUP BY n.id, n.title, n.recipient_type
        ORDER BY n.created_at DESC LIMIT 3
    """).fetchall()

    for recipient in recipients:
        print(f"  • '{recipient[0]}' sent to {recipient[1]} recipients ({recipient[2]})")

    conn.close()

    print("\n🎯 How to Use the Notification System:")
    print("1. Access the notification center from the sidebar")
    print("2. Create new notifications using the 'Create New' tab")
    print("3. View all notifications in the 'All Notifications' tab")
    print("4. Check unread notifications in the 'Unread' tab")
    print("5. Configure notification preferences in the 'Settings' tab")
    print("6. Mark notifications as read by double-clicking or using the button")
    print("7. Automatic notifications are generated for:")
    print("   - Payment reminders (7 days before due date)")
    print("   - Overdue payment warnings")
    print("   - New grade postings")
    print("   - Low attendance warnings")
    print("   - Report card generation")
    print("   - Payment confirmations")

def create_notification(title, message, notif_type, priority='normal', recipient_type='all', recipient_id=None, created_by='system', expires_days=30):
    """Create a new notification"""
    conn = get_db_connection()
    try:
        # Calculate expiration date
        expires_at = None
        if expires_days:
            expires_at = (datetime.datetime.now() + datetime.timedelta(days=expires_days)).strftime('%Y-%m-%d %H:%M:%S')

        # Insert notification
        cursor = conn.execute('''
            INSERT INTO notifications (title, message, type, priority, recipient_type, recipient_id, created_by, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, message, notif_type, priority, recipient_type, recipient_id, created_by, expires_at))

        notification_id = cursor.lastrowid

        # Create recipients based on type
        if recipient_type == 'all':
            # Get all users
            users = conn.execute('SELECT username FROM users').fetchall()
            for user in users:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, user[0]))
        elif recipient_type == 'student':
            # Get all students
            students = conn.execute('SELECT student_id FROM students').fetchall()
            for student in students:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, student[0]))
        elif recipient_type == 'admin':
            # Get all admins
            admins = conn.execute("SELECT username FROM users WHERE role = 'admin'").fetchall()
            for admin in admins:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, admin[0]))
        elif recipient_type == 'specific_student':
            # Specific student
            conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                       (notification_id, recipient_id))

        conn.commit()
        return notification_id

    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    demo_notifications()