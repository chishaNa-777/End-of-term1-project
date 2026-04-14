# Test script to verify notification system database setup

import sqlite3
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from student_managemnt import init_database

def test_notification_tables():
    """Test that all notification tables exist and have correct structure"""
    print("🧪 Testing Notification System Database Setup")
    print("=" * 60)

    # Initialize database
    init_database()

    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    # Test 1: Check if notification tables exist
    print("\n1. Checking Notification Tables Existence:")
    required_tables = [
        'notifications',
        'notification_settings',
        'notification_recipients'
    ]

    existing_tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    existing_table_names = [table[0] for table in existing_tables]

    for table in required_tables:
        if table in existing_table_names:
            print(f"   ✅ Table '{table}' exists")
        else:
            print(f"   ❌ Table '{table}' missing")

    # Test 2: Check notifications table structure
    print("\n2. Checking Notifications Table Structure:")
    c.execute("PRAGMA table_info(notifications)")
    columns = c.fetchall()

    expected_columns = {
        'id': 'INTEGER',
        'title': 'TEXT',
        'message': 'TEXT',
        'type': 'TEXT',
        'priority': 'TEXT',
        'recipient_type': 'TEXT',
        'recipient_id': 'TEXT',
        'is_read': 'BOOLEAN',
        'is_active': 'BOOLEAN',
        'created_by': 'TEXT',
        'created_at': 'TIMESTAMP',
        'expires_at': 'TIMESTAMP'
    }

    for col in columns:
        col_name, col_type = col[1], col[2]
        if col_name in expected_columns:
            if expected_columns[col_name] in col_type:
                print(f"   ✅ Column '{col_name}' ({col_type}) - OK")
            else:
                print(f"   ⚠️  Column '{col_name}' ({col_type}) - Type mismatch")
        else:
            print(f"   ℹ️  Extra column '{col_name}' ({col_type})")

    # Test 3: Check notification_settings table structure
    print("\n3. Checking Notification Settings Table Structure:")
    c.execute("PRAGMA table_info(notification_settings)")
    columns = c.fetchall()

    expected_settings_columns = {
        'id': 'INTEGER',
        'user_id': 'TEXT',
        'notification_type': 'TEXT',
        'email_enabled': 'BOOLEAN',
        'sms_enabled': 'BOOLEAN',
        'in_app_enabled': 'BOOLEAN',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP'
    }

    for col in columns:
        col_name, col_type = col[1], col[2]
        if col_name in expected_settings_columns:
            if expected_settings_columns[col_name] in col_type:
                print(f"   ✅ Column '{col_name}' ({col_type}) - OK")
            else:
                print(f"   ⚠️  Column '{col_name}' ({col_type}) - Type mismatch")

    # Test 4: Check notification_recipients table structure
    print("\n4. Checking Notification Recipients Table Structure:")
    c.execute("PRAGMA table_info(notification_recipients)")
    columns = c.fetchall()

    expected_recipients_columns = {
        'id': 'INTEGER',
        'notification_id': 'INTEGER',
        'recipient_id': 'TEXT',
        'is_read': 'BOOLEAN',
        'read_at': 'TIMESTAMP',
        'delivered_at': 'TIMESTAMP'
    }

    for col in columns:
        col_name, col_type = col[1], col[2]
        if col_name in expected_recipients_columns:
            if expected_recipients_columns[col_name] in col_type:
                print(f"   ✅ Column '{col_name}' ({col_type}) - OK")
            else:
                print(f"   ⚠️  Column '{col_name}' ({col_type}) - Type mismatch")

    # Test 5: Check default notification settings
    print("\n5. Checking Default Notification Settings:")
    settings = c.execute("SELECT notification_type, in_app_enabled FROM notification_settings WHERE user_id IS NULL").fetchall()

    if settings:
        print(f"   ✅ Found {len(settings)} default notification settings:")
        for setting in settings:
            print(f"      • {setting[0]}: In-app enabled = {bool(setting[1])}")
    else:
        print("   ❌ No default notification settings found")

    # Test 6: Test notification creation
    print("\n6. Testing Notification Creation:")
    try:
        # Insert a test notification
        c.execute('''
            INSERT INTO notifications (title, message, type, priority, recipient_type, created_by, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Test Notification', 'This is a test message', 'system', 'normal', 'all', 'test', None))

        notification_id = c.lastrowid
        print(f"   ✅ Created test notification (ID: {notification_id})")

        # Check if it was created
        notif = c.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,)).fetchone()
        if notif:
            print("   ✅ Notification retrieved successfully")
            print(f"      Title: {notif[1]}")
            print(f"      Type: {notif[3]}")
            print(f"      Priority: {notif[4]}")
        else:
            print("   ❌ Failed to retrieve notification")

        # Clean up test notification
        c.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        print("   ✅ Test notification cleaned up")

    except Exception as e:
        print(f"   ❌ Error testing notification creation: {str(e)}")

    # Test 7: Test notification functions
    print("\n7. Testing Notification Functions:")
    try:
        from student_managemnt import create_notification, generate_payment_reminders

        # Test create_notification function
        test_id = create_notification(
            "Function Test",
            "Testing notification creation function",
            "system",
            "normal",
            "all",
            None,
            "test",
            7
        )

        if test_id:
            print(f"   ✅ create_notification function works (ID: {test_id})")

            # Clean up
            c.execute("DELETE FROM notifications WHERE id = ?", (test_id,))
            c.execute("DELETE FROM notification_recipients WHERE notification_id = ?", (test_id,))
            print("   ✅ Test notification cleaned up")
        else:
            print("   ❌ create_notification function failed")

    except Exception as e:
        print(f"   ❌ Error testing notification functions: {str(e)}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("🎉 Notification system database setup test completed!")
    print("\nIf all tests passed, the notification system is ready to use.")
    print("You can now:")
    print("• Run the main application to access the notification center")
    print("• Use demo_notifications.py to see sample notifications")
    print("• Create automated notifications through the system")

if __name__ == "__main__":
    test_notification_tables()