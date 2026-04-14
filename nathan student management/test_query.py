import sqlite3

conn = sqlite3.connect('student_db.sqlite')
c = conn.cursor()

print("Testing parent query...")
parents = c.execute('''
    SELECT u.username, u.role, ps.student_id, s.name as student_name
    FROM users u
    JOIN parent_students ps ON u.id = ps.parent_user_id
    JOIN students s ON ps.student_id = s.student_id
    WHERE u.role = 'parent'
    ORDER BY u.username
''').fetchall()

print(f'Parents found: {len(parents)}')
for parent in parents:
    print(f'  {parent}')

conn.close()