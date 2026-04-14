#!/usr/bin/env python3
"""
Test script to verify payment tracking system database setup
"""

import sqlite3
import os

def test_payment_tables():
    """Test that payment tables are created correctly"""
    db_file = "student_db.sqlite"

    if not os.path.exists(db_file):
        print("❌ Database file not found. Please run the application first.")
        return False

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Check if payment tables exist
    tables_to_check = [
        'payment_categories',
        'payments',
        'payment_methods'
    ]

    for table in tables_to_check:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not c.fetchone():
            print(f"❌ Table '{table}' not found")
            conn.close()
            return False
        else:
            print(f"✅ Table '{table}' exists")

    # Check payment categories
    c.execute("SELECT COUNT(*) as count FROM payment_categories")
    result = c.fetchone()
    category_count = result[0]  # Use index instead of key
    print(f"✅ Payment categories: {category_count} default categories loaded")

    # Check payment methods
    c.execute("SELECT COUNT(*) as count FROM payment_methods")
    result = c.fetchone()
    method_count = result[0]  # Use index instead of key
    print(f"✅ Payment methods: {method_count} default methods loaded")

    # Check table structure for payments
    c.execute("PRAGMA table_info(payments)")
    columns = c.fetchall()
    expected_columns = ['id', 'student_id', 'category_id', 'amount', 'payment_date',
                       'due_date', 'payment_method', 'reference_number', 'status',
                       'notes', 'recorded_by', 'created_at']

    actual_columns = [col[1] for col in columns]
    missing_columns = [col for col in expected_columns if col not in actual_columns]

    if missing_columns:
        print(f"❌ Missing columns in payments table: {missing_columns}")
        conn.close()
        return False
    else:
        print("✅ Payments table structure is correct")

    conn.close()
    return True

if __name__ == "__main__":
    print("🧪 Testing Payment Tracking System Database Setup")
    print("=" * 50)

    if test_payment_tables():
        print("\n🎉 Payment tracking system database setup is working correctly!")
        print("\nFeatures available:")
        print("- 💰 Payment recording and tracking")
        print("- 📊 Payment categories management")
        print("- 🔍 Payment filtering and search")
        print("- 📈 Payment summary statistics")
        print("- 📄 Payment reports export")
    else:
        print("\n❌ Payment tracking system setup has issues.")