# Comprehensive Notification System Demo
# This script demonstrates all notification system features

import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from student_managemnt import init_database, create_notification

def comprehensive_notification_demo():
    """Demonstrate the complete notification system functionality"""
    print("🔔 Comprehensive Notification System Demo")
    print("=" * 70)

    # Initialize database
    print("\n📊 Initializing database...")
    init_database()

    # Connect to database
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    # Clear any existing demo notifications
    c.execute("DELETE FROM notifications WHERE created_by = 'demo'")
    c.execute("DELETE FROM notification_recipients WHERE notification_id IN (SELECT id FROM notifications WHERE created_by = 'demo')")
    conn.commit()

    print("✅ Database initialized and cleaned")

    # Demo 1: Create various types of notifications
    print("\n📝 Creating Sample Notifications...")

    notifications_created = []

    # System announcement
    notif_id = create_notification(
        "🎓 Welcome to Student Management System",
        "Welcome to our enhanced student management system! We now have automated notifications for payments, grades, and important announcements.",
        "system",
        "normal",
        "all",
        None,
        "demo",
        30  # 30 days expiry
    )
    if notif_id:
        notifications_created.append(("System Announcement", notif_id))

    # Payment reminder
    notif_id = create_notification(
        "💰 Payment Reminder",
        "Your tuition payment is due in 7 days. Please ensure timely payment to avoid late fees.",
        "payment",
        "high",
        "specific",
        "STU001",  # Specific student
        "demo",
        7
    )
    if notif_id:
        notifications_created.append(("Payment Reminder", notif_id))

    # Grade notification
    notif_id = create_notification(
        "📚 Grade Posted",
        "Your grade for Mathematics (MATH101) has been posted. You scored an A-. Keep up the good work!",
        "grade",
        "normal",
        "specific",
        "STU002",  # Another student
        "demo",
        14
    )
    if notif_id:
        notifications_created.append(("Grade Notification", notif_id))

    # Attendance warning
    notif_id = create_notification(
        "⚠️ Attendance Warning",
        "You have missed 3 classes this week. Please maintain regular attendance to stay eligible for exams.",
        "attendance",
        "high",
        "specific",
        "STU001",
        "demo",
        3
    )
    if notif_id:
        notifications_created.append(("Attendance Warning", notif_id))

    # Report card ready
    notif_id = create_notification(
        "📄 Report Card Available",
        "Your semester report card is now available for download. Please review your academic performance.",
        "report",
        "normal",
        "specific",
        "STU002",
        "demo",
        60
    )
    if notif_id:
        notifications_created.append(("Report Card Ready", notif_id))

    print(f"✅ Created {len(notifications_created)} sample notifications")

    # Demo 2: Show notification statistics
    print("\n📊 Notification Statistics:")

    # Total notifications
    total = c.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
    print(f"   • Total notifications: {total}")

    # By type
    types = c.execute("SELECT type, COUNT(*) FROM notifications GROUP BY type").fetchall()
    print("   • By type:")
    for notif_type, count in types:
        print(f"     - {notif_type}: {count}")

    # By priority
    priorities = c.execute("SELECT priority, COUNT(*) FROM notifications GROUP BY priority").fetchall()
    print("   • By priority:")
    for priority, count in priorities:
        print(f"     - {priority}: {count}")

    # Unread notifications
    unread = c.execute("SELECT COUNT(*) FROM notification_recipients WHERE is_read = 0").fetchone()[0]
    print(f"   • Unread notifications: {unread}")

    # Demo 3: Show notification details
    print("\n📋 Recent Notifications:")

    recent = c.execute("""
        SELECT n.id, n.title, n.type, n.priority, n.created_at, COUNT(nr.id) as recipients
        FROM notifications n
        LEFT JOIN notification_recipients nr ON n.id = nr.notification_id
        WHERE n.created_by = 'demo'
        GROUP BY n.id
        ORDER BY n.created_at DESC
        LIMIT 5
    """).fetchall()

    for notif in recent:
        notif_id, title, notif_type, priority, created_at, recipients = notif
        print(f"   • ID {notif_id}: {title}")
        print(f"     Type: {notif_type} | Priority: {priority} | Recipients: {recipients}")
        print(f"     Created: {created_at}")

    # Demo 4: Show notification settings
    print("\n⚙️ Notification Settings:")

    settings = c.execute("""
        SELECT notification_type, COUNT(*) as users_with_setting
        FROM notification_settings
        WHERE in_app_enabled = 1
        GROUP BY notification_type
        ORDER BY notification_type
    """).fetchall()

    print("   • In-app notifications enabled for:")
    for setting_type, count in settings:
        print(f"     - {setting_type}: {count} users")

    # Demo 5: Simulate marking notifications as read
    print("\n👀 Simulating User Reading Notifications:")

    # Mark first notification as read for STU001
    c.execute("""
        UPDATE notification_recipients
        SET is_read = 1, read_at = ?
        WHERE notification_id = 1 AND recipient_id = 'STU001'
    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))

    # Mark attendance warning as read
    attendance_notif = c.execute("SELECT id FROM notifications WHERE type = 'attendance' AND created_by = 'demo'").fetchone()
    if attendance_notif:
        c.execute("""
            UPDATE notification_recipients
            SET is_read = 1, read_at = ?
            WHERE notification_id = ? AND recipient_id = 'STU001'
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), attendance_notif[0]))

    conn.commit()

    # Show updated unread count
    unread_after = c.execute("SELECT COUNT(*) FROM notification_recipients WHERE is_read = 0").fetchone()[0]
    print(f"   • Unread notifications after reading: {unread_after}")

    # Demo 6: Show notification expiry
    print("\n⏰ Notification Expiry Information:")

    # Check for expiring notifications
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    expiring = c.execute("""
        SELECT COUNT(*) FROM notifications
        WHERE expires_at IS NOT NULL
        AND date(expires_at) = date(?)
    """, (tomorrow,)).fetchone()[0]

    print(f"   • Notifications expiring tomorrow: {expiring}")

    # Demo 7: Show automated notification generation examples
    print("\n🤖 Automated Notification Generation Examples:")
    print("   • Payment reminders: Generated when payments are due")
    print("   • Grade notifications: Created when grades are posted")
    print("   • Attendance warnings: Triggered by low attendance")
    print("   • Report card alerts: Sent when report cards are ready")
    print("   • System announcements: For important updates")

    conn.close()

    print("\n" + "=" * 70)
    print("🎉 Notification System Demo Complete!")
    print("\n✨ Key Features Demonstrated:")
    print("   ✅ Database schema with proper relationships")
    print("   ✅ Multiple notification types and priorities")
    print("   ✅ Recipient management and tracking")
    print("   ✅ Notification settings and preferences")
    print("   ✅ Read/unread status tracking")
    print("   ✅ Expiry date management")
    print("   ✅ Automated notification generation")
    print("\n🚀 Ready to use in the main application!")
    print("   Run student_managemnt.py and click '🔔 Notifications' to explore the UI")

if __name__ == "__main__":
    comprehensive_notification_demo()