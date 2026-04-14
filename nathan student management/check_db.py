import sqlite3
import hashlib

conn = sqlite3.connect('student_db.sqlite')
users = conn.execute('SELECT username, password FROM users WHERE role="parent"').fetchall()
print('Parent users:')
for u in users:
    print(f'{u[0]}: {u[1]}')

# Test password hash
test_pass = 'john123'
hashed = hashlib.sha256(test_pass.encode()).hexdigest()
print(f'\nSHA256 hash for "john123": {hashed}')

conn.close()