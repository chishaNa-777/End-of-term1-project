#!/usr/bin/env python3
"""
Test script to verify gradebook and report cards system database setup
"""

import sqlite3
import os

def test_gradebook_tables():
    """Test that gradebook tables are created correctly"""

    db_file = "student_db.sqlite"

    if not os.path.exists(db_file):
        print("❌ Database file not found. Please run the application first.")
        return False

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Check if gradebook tables exist
    tables_to_check = [
        'academic_years',
        'gradebook_categories',
        'gradebook_assessments',
        'gradebook_grades',
        'report_cards',
        'report_card_details'
    ]

    for table in tables_to_check:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not c.fetchone():
            print(f"❌ Table '{table}' not found")
            conn.close()
            return False
        else:
            print(f"✅ Table '{table}' exists")

    # Check academic years
    c.execute("SELECT COUNT(*) FROM academic_years")
    year_count = c.fetchone()[0]
    print(f"✅ Academic years: {year_count} years configured")

    # Check gradebook categories
    c.execute("SELECT COUNT(*) FROM gradebook_categories")
    category_count = c.fetchone()[0]
    print(f"✅ Gradebook categories: {category_count} categories loaded")

    # Check default categories
    c.execute("SELECT name FROM gradebook_categories ORDER BY name")
    categories = [row[0] for row in c.fetchall()]
    expected_categories = ['Assignments', 'Final Exam', 'Midterm Exam', 'Quizzes']
    missing_categories = [cat for cat in expected_categories if cat not in categories]

    if missing_categories:
        print(f"⚠️  Missing default categories: {missing_categories}")
    else:
        print("✅ Default gradebook categories loaded")

    # Check table structures
    tables_structure = {
        'gradebook_grades': ['id', 'student_id', 'assessment_id', 'score', 'grade_letter', 'comments', 'recorded_by', 'recorded_at'],
        'report_cards': ['id', 'student_id', 'academic_year_id', 'semester', 'gpa', 'total_credits', 'status', 'generated_by', 'generated_at'],
        'report_card_details': ['id', 'report_card_id', 'subject_name', 'final_grade', 'score', 'credits', 'comments']
    }

    for table, expected_cols in tables_structure.items():
        c.execute(f"PRAGMA table_info({table})")
        actual_cols = [row[1] for row in c.fetchall()]
        missing_cols = [col for col in expected_cols if col not in actual_cols]

        if missing_cols:
            print(f"❌ Missing columns in {table}: {missing_cols}")
            conn.close()
            return False
        else:
            print(f"✅ {table} structure is correct")

    conn.close()
    return True

def create_sample_gradebook_data():
    """Create sample gradebook data for testing"""
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    # Check if we have students
    c.execute("SELECT student_id FROM students LIMIT 1")
    if not c.fetchone():
        print("⚠️  No students found. Add some students first to test gradebook.")
        conn.close()
        return

    # Check if we have assessments
    c.execute("SELECT id FROM gradebook_assessments LIMIT 1")
    if not c.fetchone():
        # Create a sample assessment
        c.execute("SELECT id FROM gradebook_categories WHERE name = 'Assignments' LIMIT 1")
        category = c.fetchone()
        if category:
            c.execute("""
                INSERT INTO gradebook_assessments (category_id, assessment_name, max_score, weight, assessment_date)
                VALUES (?, ?, ?, ?, ?)
            """, (category[0], 'Sample Assignment 1', 100.0, 1.0, '2024-01-15'))

            assessment_id = c.lastrowid

            # Add sample grades for first student
            c.execute("SELECT student_id FROM students LIMIT 1")
            student = c.fetchone()
            if student:
                c.execute("""
                    INSERT INTO gradebook_grades (student_id, assessment_id, score, grade_letter, recorded_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (student[0], assessment_id, 85.0, 'B', 'System'))

                print("✅ Sample gradebook data created")
        else:
            print("⚠️  Could not create sample assessment - no categories found")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("📓 Testing Gradebook & Report Cards System Database Setup")
    print("=" * 60)

    if test_gradebook_tables():
        print("\n🎉 Gradebook & Report Cards system database setup is working correctly!")
        print("\nFeatures available:")
        print("- 📝 Grade entry and management")
        print("- 📊 GPA calculation and analytics")
        print("- 📄 Automated report card generation")
        print("- 📅 Academic year and semester tracking")
        print("- 📈 Performance analytics and statistics")

        # Create sample data if none exists
        create_sample_gradebook_data()

    else:
        print("\n❌ Gradebook & Report Cards system setup has issues.")