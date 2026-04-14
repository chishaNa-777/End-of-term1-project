#!/usr/bin/env python3
"""
Payment Tracking System Demo
This script demonstrates how to use the payment tracking features programmatically.
"""

import sqlite3
import datetime

def demo_payment_operations():
    """Demonstrate payment tracking operations"""

    # Connect to database
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    print("💰 Payment Tracking System Demo")
    print("=" * 40)

    # 1. Show available payment categories
    print("\n📋 Available Payment Categories:")
    categories = c.execute("SELECT name, description, default_amount FROM payment_categories WHERE is_active = 1").fetchall()
    for cat in categories:
        print(f"  • {cat[0]}: {cat[1]} (${cat[2]:.2f})")

    # 2. Show available payment methods
    print("\n💳 Available Payment Methods:")
    methods = c.execute("SELECT name, description FROM payment_methods WHERE is_active = 1").fetchall()
    for method in methods:
        print(f"  • {method[0]}: {method[1]}")

    # 3. Show sample students (if any exist)
    print("\n👥 Sample Students:")
    students = c.execute("SELECT student_id, name FROM students LIMIT 5").fetchall()
    if students:
        for student in students:
            print(f"  • {student[0]}: {student[1]}")
    else:
        print("  No students found. Add some students first!")

    # 4. Show payment statistics
    print("\n📊 Payment Statistics:")
    stats = c.execute("""
        SELECT
            COUNT(*) as total_payments,
            SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END) as total_paid,
            SUM(CASE WHEN status = 'Pending' THEN amount ELSE 0 END) as total_pending,
            SUM(CASE WHEN status = 'Overdue' THEN amount ELSE 0 END) as total_overdue
        FROM payments
    """).fetchone()

    print(f"  • Total Payments: {stats[0]}")
    print(f"  • Total Paid: ${stats[1] or 0:.2f}")
    print(f"  • Total Pending: ${stats[2] or 0:.2f}")
    print(f"  • Total Overdue: ${stats[3] or 0:.2f}")

    # 5. Show recent payments
    print("\n🕒 Recent Payments:")
    recent = c.execute("""
        SELECT p.amount, pc.name as category, s.name as student_name,
               p.status, p.payment_date
        FROM payments p
        JOIN payment_categories pc ON p.category_id = pc.id
        JOIN students s ON p.student_id = s.student_id
        ORDER BY p.created_at DESC LIMIT 5
    """).fetchall()

    if recent:
        for payment in recent:
            print(f"  • ${payment[0]:.2f} - {payment[1]} for {payment[2]} ({payment[3]}) - {payment[4] or 'N/A'}")
    else:
        print("  No payments recorded yet.")

    conn.close()

    print("\n🎯 How to Use Payment Tracking:")
    print("1. Launch the application and login")
    print("2. Click 'Payment Tracking' in the sidebar")
    print("3. Click 'Record Payment' to add new payments")
    print("4. Use filters to view specific payments")
    print("5. Click 'Export Report' to generate CSV reports")
    print("6. Monitor summary statistics at the bottom")

def create_sample_payment():
    """Create a sample payment for demonstration"""
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    # Check if we have students and categories
    student = c.execute("SELECT student_id FROM students LIMIT 1").fetchone()
    category = c.execute("SELECT id FROM payment_categories WHERE name = 'Tuition Fee'").fetchone()

    if student and category:
        # Create a sample payment
        c.execute("""
            INSERT INTO payments (student_id, category_id, amount, payment_date, due_date,
                               payment_method, status, reference_number, notes, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student[0], category[0], 2500.00, datetime.date.today().strftime('%Y-%m-%d'),
              (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
              'Bank Transfer', 'Paid', 'TXN-2024-001', 'Sample payment for demo', 'System'))

        conn.commit()
        print("✅ Sample payment created for demonstration!")
    else:
        print("⚠️  Cannot create sample payment: No students or categories found.")

    conn.close()

if __name__ == "__main__":
    # Create sample payment if database is empty
    conn = sqlite3.connect("student_db.sqlite")
    payment_count = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
    conn.close()

    if payment_count == 0:
        create_sample_payment()

    demo_payment_operations()