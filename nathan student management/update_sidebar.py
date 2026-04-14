with open('student_managemnt.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the sidebar menu items
content = content.replace('            ("� Payment Tracking", self.show_payments),', '            ("💰 Payment Tracking", self.show_payments),')
content = content.replace('            ("�📚 Subjects & Marks", self.show_subjects),', '            ("📚 Subjects & Marks", self.show_subjects),')
content = content.replace('            ("� Tutorials", self.show_tutorials),', '            ("🎥 Tutorials", self.show_tutorials),')
content = content.replace('            ("�📅 Attendance", self.show_attendance),', '            ("📅 Attendance", self.show_attendance),')

# Insert gradebook and notifications after payment tracking
old_text = '''            ("💰 Payment Tracking", self.show_payments),
            ("📚 Subjects & Marks", self.show_subjects),'''

new_text = '''            ("💰 Payment Tracking", self.show_payments),
            ("📓 Gradebook", self.show_gradebook),
            ("🔔 Notifications", self.show_notifications),
            ("📚 Subjects & Marks", self.show_subjects),'''

content = content.replace(old_text, new_text)

with open('student_managemnt.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Sidebar menu updated successfully!')