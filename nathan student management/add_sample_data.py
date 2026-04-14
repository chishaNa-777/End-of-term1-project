import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('student_db.sqlite')
c = conn.cursor()

# Sample students data
sample_students = [
    ('STU001', 'John Smith', 'john.smith@email.com', '+260-211-123456', 'Male', '2005-03-15', '123 Main St, Lusaka', 'Computer Science', '2024-09-01', 'Active', 'Mary Smith', '+260-211-123457'),
    ('STU002', 'Sarah Johnson', 'sarah.johnson@email.com', '+260-211-234567', 'Female', '2004-07-22', '456 Oak Ave, Lusaka', 'Business Administration', '2024-09-01', 'Active', 'Michael Johnson', '+260-211-234568'),
    ('STU003', 'David Brown', 'david.brown@email.com', '+260-211-345678', 'Male', '2005-11-08', '789 Pine St, Lusaka', 'Electrical Engineering', '2024-09-01', 'Active', 'Lisa Brown', '+260-211-345679'),
]

print("Adding sample students...")

for student in sample_students:
    try:
        c.execute('''
            INSERT INTO students (student_id, name, email, phone, gender, dob, address, program, enrollment_date, status, guardian_name, guardian_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student)
        print(f"✅ Added student: {student[1]} ({student[0]})")
    except sqlite3.IntegrityError:
        print(f"⚠️  Student {student[0]} already exists - skipping")

# Add some sample grades
sample_grades = [
    ('STU001', 'Mathematics', 85.5, 3.0, '2024-2025'),
    ('STU001', 'Computer Science', 92.0, 4.0, '2024-2025'),
    ('STU001', 'English', 78.5, 2.0, '2024-2025'),
    ('STU002', 'Business Math', 88.0, 3.0, '2024-2025'),
    ('STU002', 'Marketing', 91.5, 3.0, '2024-2025'),
    ('STU002', 'Accounting', 85.0, 3.0, '2024-2025'),
    ('STU003', 'Physics', 87.5, 4.0, '2024-2025'),
    ('STU003', 'Electrical Circuits', 89.0, 4.0, '2024-2025'),
    ('STU003', 'Programming', 94.5, 3.0, '2024-2025'),
]

print("\nAdding sample grades...")
for grade in sample_grades:
    c.execute('''
        INSERT INTO subjects (student_id, subject_name, marks, credits, semester)
        VALUES (?, ?, ?, ?, ?)
    ''', grade)
    print(f"✅ Added grade: {grade[1]} for {grade[0]}")

# Add some sample payments
sample_payments = [
    ('STU001', 1, 5000.00, '2024-09-01', '2024-09-15', 'Bank Transfer', 'TXN001', 'Paid'),
    ('STU001', 2, 2000.00, '2024-09-01', '2024-10-01', None, None, 'Pending'),
    ('STU002', 1, 5000.00, '2024-09-01', '2024-09-15', 'Cash', 'TXN002', 'Paid'),
    ('STU002', 3, 200.00, '2024-09-01', '2024-09-30', None, None, 'Pending'),
    ('STU003', 1, 5000.00, '2024-09-01', '2024-09-15', 'Mobile Money', 'TXN003', 'Paid'),
]

print("\nAdding sample payments...")
for payment in sample_payments:
    c.execute('''
        INSERT INTO payments (student_id, category_id, amount, payment_date, due_date, payment_method, reference_number, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', payment)
    print(f"✅ Added payment: ${payment[2]} for {payment[0]}")

# Add some sample attendance
sample_attendance = []
import random
for student_id in ['STU001', 'STU002', 'STU003']:
    for i in range(10):  # 10 days of attendance
        date = f'2024-09-{i+1:02d}'
        status = random.choice(['Present', 'Present', 'Present', 'Present', 'Absent'])  # 80% present rate
        sample_attendance.append((student_id, date, status, ''))

print("\nAdding sample attendance...")
for attendance in sample_attendance:
    c.execute('''
        INSERT INTO attendance (student_id, date, status, remarks)
        VALUES (?, ?, ?, ?)
    ''', attendance)

print(f"✅ Added {len(sample_attendance)} attendance records")

conn.commit()
conn.close()

print("\n🎉 Sample data added successfully!")
print("Now you can run the parent portal setup script.")