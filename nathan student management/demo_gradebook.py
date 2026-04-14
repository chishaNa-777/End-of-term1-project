#!/usr/bin/env python3
"""
Gradebook & Report Cards System Demo
This script demonstrates how to use the gradebook and report cards features.
"""

import sqlite3
import datetime

def demo_gradebook_operations():
    """Demonstrate gradebook operations"""

    # Connect to database
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    print("📓 Gradebook & Report Cards System Demo")
    print("=" * 50)

    # 1. Show academic years
    print("\n📅 Academic Years:")
    years = c.execute("SELECT year_name, start_date, end_date, is_current FROM academic_years ORDER BY start_date DESC").fetchall()
    for year in years:
        current = " (Current)" if year[3] else ""
        print(f"  • {year[0]}{current}: {year[1]} to {year[2]}")

    # 2. Show gradebook categories
    print("\n📂 Gradebook Categories:")
    categories = c.execute("SELECT name, description, weight FROM gradebook_categories WHERE is_active = 1 ORDER BY name").fetchall()
    for cat in categories:
        print(f"  • {cat[0]}: {cat[1]} (Weight: {cat[2]})")

    # 3. Show assessments
    print("\n📝 Assessments:")
    assessments = c.execute("""
        SELECT ga.assessment_name, gc.name as category_name, ga.max_score, ga.weight, ga.assessment_date
        FROM gradebook_assessments ga
        JOIN gradebook_categories gc ON ga.category_id = gc.id
        WHERE ga.is_active = 1
        ORDER BY ga.assessment_date
    """).fetchall()

    if assessments:
        for assessment in assessments:
            date_display = assessment[4] or "No date"
            print(f"  • {assessment[0]} ({assessment[1]}): Max {assessment[2]}, Weight {assessment[3]} - {date_display}")
    else:
        print("  No assessments created yet.")

    # 4. Show grades
    print("\n📊 Grades Entered:")
    grades = c.execute("""
        SELECT s.name, ga.assessment_name, gg.score, gg.grade_letter, gg.recorded_at
        FROM gradebook_grades gg
        JOIN students s ON gg.student_id = s.student_id
        JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
        ORDER BY gg.recorded_at DESC
        LIMIT 10
    """).fetchall()

    if grades:
        for grade in grades:
            date_display = grade[4][:10] if grade[4] else "N/A"
            print(f"  • {grade[0]}: {grade[1]} - {grade[2]}/100 ({grade[3]}) - {date_display}")
    else:
        print("  No grades entered yet.")

    # 5. Show report cards
    print("\n📄 Report Cards Generated:")
    report_cards = c.execute("""
        SELECT s.name, ay.year_name, rc.semester, rc.gpa, rc.generated_at
        FROM report_cards rc
        JOIN students s ON rc.student_id = s.student_id
        JOIN academic_years ay ON rc.academic_year_id = ay.id
        ORDER BY rc.generated_at DESC
        LIMIT 5
    """).fetchall()

    if report_cards:
        for rc in report_cards:
            date_display = rc[4][:10] if rc[4] else "N/A"
            gpa_display = f"{rc[3]:.2f}" if rc[3] else "N/A"
            print(f"  • {rc[0]}: {rc[1]} ({rc[2]}) - GPA {gpa_display} - {date_display}")
    else:
        print("  No report cards generated yet.")

    # 6. Show GPA statistics
    print("\n📈 GPA Statistics:")
    stats = c.execute("""
        SELECT
            COUNT(*) as total_reports,
            AVG(gpa) as avg_gpa,
            MAX(gpa) as max_gpa,
            MIN(gpa) as min_gpa
        FROM report_cards
        WHERE gpa IS NOT NULL
    """).fetchone()

    if stats[0] > 0:
        print(f"  • Total Report Cards: {stats[0]}")
        print(f"  • Average GPA: {stats[1]:.2f}")
        print(f"  • Highest GPA: {stats[2]:.2f}")
        print(f"  • Lowest GPA: {stats[3]:.2f}")
    else:
        print("  No GPA data available yet.")

    conn.close()

    print("\n🎯 How to Use Gradebook & Report Cards:")
    print("1. Launch the application and login")
    print("2. Click 'Gradebook' in the sidebar")
    print("3. Use the three tabs:")
    print("   • Grade Entry: Enter and view student grades")
    print("   • Report Cards: Generate and view report cards")
    print("   • Assessment Setup: Configure categories and assessments")
    print("4. Calculate GPA for individual students")
    print("5. View grade analytics and performance statistics")
    print("6. Generate comprehensive report cards")

def create_sample_assessment():
    """Create a sample assessment for demonstration"""
    conn = sqlite3.connect("student_db.sqlite")
    c = conn.cursor()

    # Check if we have categories
    c.execute("SELECT id FROM gradebook_categories WHERE name = 'Quizzes' LIMIT 1")
    category = c.fetchone()

    if category:
        # Create sample assessment
        c.execute("""
            INSERT INTO gradebook_assessments (category_id, assessment_name, max_score, weight, assessment_date)
            VALUES (?, ?, ?, ?, ?)
        """, (category[0], 'Mathematics Quiz 1', 50.0, 0.5, '2024-01-20'))

        assessment_id = c.lastrowid

        # Add sample grades
        c.execute("SELECT student_id FROM students LIMIT 3")
        students = c.fetchall()

        sample_grades = [42.0, 48.0, 35.0]  # Sample scores

        for i, student in enumerate(students):
            if i < len(sample_grades):
                grade_letter = 'A' if sample_grades[i] >= 45 else 'B' if sample_grades[i] >= 40 else 'C'
                c.execute("""
                    INSERT INTO gradebook_grades (student_id, assessment_id, score, grade_letter, recorded_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (student[0], assessment_id, sample_grades[i], grade_letter, 'System'))

        print("✅ Sample assessment and grades created")
    else:
        print("⚠️  Could not create sample assessment - no quiz category found")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Create sample data if needed
    conn = sqlite3.connect("student_db.sqlite")
    assessment_count = conn.execute("SELECT COUNT(*) FROM gradebook_assessments").fetchone()[0]
    conn.close()

    if assessment_count == 0:
        create_sample_assessment()

    demo_gradebook_operations()