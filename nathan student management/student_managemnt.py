import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import hashlib
import csv
import os
import sys                     # Added for restart functionality
import random
import datetime
import shutil
from collections import Counter

# Try to import matplotlib for charts (Optional feature)
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ==========================================
# 1. DATABASE & CORE ENGINE (SQLite Backend)
# ==========================================

DB_FILE = "student_db.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )''')
    
    # 2. Students Table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    gender TEXT,
                    dob TEXT,
                    address TEXT,
                    program TEXT,
                    enrollment_date TEXT,
                    status TEXT DEFAULT 'Active',
                    guardian_name TEXT,
                    guardian_phone TEXT,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Add image_path column if not exists (for existing databases)
    try:
        c.execute("ALTER TABLE students ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # 3. Subjects Table
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    marks REAL NOT NULL,
                    credits REAL DEFAULT 3.0,
                    semester TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(student_id)
                )''')

    # 4. Tutorials Table
    c.execute('''CREATE TABLE IF NOT EXISTS tutorials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    video_url TEXT,
                    uploaded_by TEXT,
                    subject TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # 5. Study Notes Table
    c.execute('''CREATE TABLE IF NOT EXISTS study_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    subject TEXT,
                    file_path TEXT,
                    uploaded_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # 6. Attendance Table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT CHECK(status IN ('Present', 'Absent', 'Late')),
                    remarks TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(student_id)
                )''')
    
    # 5. Audit Logs
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # 6. Settings
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )''')

    # 7. Payment Categories Table
    c.execute('''CREATE TABLE IF NOT EXISTS payment_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    default_amount REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # 8. Payments Table
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    due_date TEXT,
                    payment_method TEXT,
                    reference_number TEXT,
                    status TEXT CHECK(status IN ('Pending', 'Paid', 'Overdue', 'Cancelled')) DEFAULT 'Pending',
                    notes TEXT,
                    recorded_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    FOREIGN KEY(category_id) REFERENCES payment_categories(id)
                )''')

    # 9. Payment Methods Table
    c.execute('''CREATE TABLE IF NOT EXISTS payment_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1
                )''')

    # Insert default payment categories
    default_categories = [
        ('Tuition Fee', 'Regular tuition fees', 5000.00),
        ('Registration Fee', 'One-time registration fee', 2000.00),
        ('Library Fee', 'Library access fee', 200.00),
        ('Laboratory Fee', 'Lab equipment and materials', 300.00),
        ('Sports Fee', 'Sports and recreational activities', 150.00),
        ('Transportation Fee', 'School transport fee', 400.00),
        ('Materials Fee', 'Study materials and books', 250.00),
        ('Examination Fee', 'Exam registration fee', 100.00)
    ]

    for category in default_categories:
        try:
            c.execute("INSERT INTO payment_categories (name, description, default_amount) VALUES (?, ?, ?)", category)
        except sqlite3.IntegrityError:
            pass  # Category already exists

    # Insert default payment methods
    default_methods = [
        ('Cash', 'Cash payment'),
        ('Bank Transfer', 'Direct bank transfer'),
        ('Zanaco Bank', 'Zanaco Bank transfer'),
        ('Credit Card', 'Credit card payment'),
        ('Debit Card', 'Debit card payment'),
        ('Mobile Money', 'Mobile money transfer'),
        ('Airtel Money', 'Airtel Money mobile payment'),
        ('Cheque', 'Bank cheque'),
        ('Scholarship', 'Scholarship payment'),
        ('Installment', 'Payment in installments')
    ]

    for method in default_methods:
        try:
            c.execute("INSERT INTO payment_methods (name, description) VALUES (?, ?)", method)
        except sqlite3.IntegrityError:
            pass  # Method already exists

    # 10. Academic Years Table
    c.execute('''CREATE TABLE IF NOT EXISTS academic_years (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year_name TEXT UNIQUE NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    is_current BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # 11. Gradebook Categories Table
    c.execute('''CREATE TABLE IF NOT EXISTS gradebook_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    weight REAL DEFAULT 1.0,
                    academic_year_id INTEGER,
                    subject_name TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(academic_year_id) REFERENCES academic_years(id)
                )''')

    # 12. Gradebook Assessments Table
    c.execute('''CREATE TABLE IF NOT EXISTS gradebook_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    assessment_name TEXT NOT NULL,
                    description TEXT,
                    max_score REAL DEFAULT 100.0,
                    weight REAL DEFAULT 1.0,
                    assessment_date TEXT,
                    due_date TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(category_id) REFERENCES gradebook_categories(id)
                )''')

    # 13. Gradebook Grades Table
    c.execute('''CREATE TABLE IF NOT EXISTS gradebook_grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    assessment_id INTEGER NOT NULL,
                    score REAL,
                    grade_letter TEXT,
                    comments TEXT,
                    recorded_by TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    FOREIGN KEY(assessment_id) REFERENCES gradebook_assessments(id),
                    UNIQUE(student_id, assessment_id)
                )''')

    # 14. Report Cards Table
    c.execute('''CREATE TABLE IF NOT EXISTS report_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    academic_year_id INTEGER NOT NULL,
                    semester TEXT,
                    gpa REAL,
                    total_credits REAL DEFAULT 0,
                    status TEXT DEFAULT 'Draft',
                    generated_by TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    FOREIGN KEY(academic_year_id) REFERENCES academic_years(id)
                )''')

    # 15. Report Card Details Table
    c.execute('''CREATE TABLE IF NOT EXISTS report_card_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_card_id INTEGER NOT NULL,
                    subject_name TEXT NOT NULL,
                    final_grade TEXT,
                    score REAL,
                    credits REAL DEFAULT 3.0,
                    comments TEXT,
                    FOREIGN KEY(report_card_id) REFERENCES report_cards(id)
                )''')

    # 16. Notifications Table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,  -- 'payment', 'grade', 'attendance', 'system', 'announcement'
                    priority TEXT DEFAULT 'normal',  -- 'low', 'normal', 'high', 'urgent'
                    recipient_type TEXT NOT NULL,  -- 'all', 'student', 'admin', 'specific_student'
                    recipient_id TEXT,  -- student_id for specific notifications
                    is_read BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )''')

    # 17. Notification Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS notification_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    notification_type TEXT NOT NULL,
                    email_enabled BOOLEAN DEFAULT 0,
                    sms_enabled BOOLEAN DEFAULT 0,
                    in_app_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, notification_type)
                )''')

    # 18. Notification Recipients Table (for tracking who received what)
    c.execute('''CREATE TABLE IF NOT EXISTS notification_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_id INTEGER NOT NULL,
                    recipient_id TEXT NOT NULL,  -- student_id or user_id
                    is_read BOOLEAN DEFAULT 0,
                    read_at TIMESTAMP,
                    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(notification_id) REFERENCES notifications(id)
                )''')

    # 19. Parent-Student Relationships Table
    c.execute('''CREATE TABLE IF NOT EXISTS parent_students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_user_id INTEGER NOT NULL,
                    student_id TEXT NOT NULL,
                    relationship TEXT DEFAULT 'Parent',  -- Parent, Guardian, etc.
                    is_primary BOOLEAN DEFAULT 1,
                    can_view_grades BOOLEAN DEFAULT 1,
                    can_view_payments BOOLEAN DEFAULT 1,
                    can_view_attendance BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(parent_user_id) REFERENCES users(id),
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    UNIQUE(parent_user_id, student_id)
                )''')

    # 20. Parent Messages Table (for communication between parents and admins)
    c.execute('''CREATE TABLE IF NOT EXISTS parent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER,
                    student_id TEXT,  -- Related student if applicable
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'general',  -- 'general', 'complaint', 'inquiry', 'praise'
                    priority TEXT DEFAULT 'normal',  -- 'low', 'normal', 'high', 'urgent'
                    status TEXT DEFAULT 'unread',  -- 'unread', 'read', 'replied', 'closed'
                    admin_response TEXT,
                    admin_response_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(from_user_id) REFERENCES users(id),
                    FOREIGN KEY(to_user_id) REFERENCES users(id),
                    FOREIGN KEY(student_id) REFERENCES students(student_id)
                )''')

    # Insert default academic year
    current_year = datetime.date.today().year
    try:
        c.execute("INSERT INTO academic_years (year_name, start_date, end_date, is_current) VALUES (?, ?, ?, ?)",
                 (f"{current_year}-{current_year+1}", f"{current_year}-09-01", f"{current_year+1}-06-30", 1))
    except sqlite3.IntegrityError:
        pass  # Academic year already exists

    # Insert default gradebook categories
    default_grade_categories = [
        ('Assignments', 'Homework and assignments', 0.3),
        ('Quizzes', 'Short quizzes and tests', 0.2),
        ('Midterm Exam', 'Midterm examination', 0.2),
        ('Final Exam', 'Final examination', 0.3)
    ]

    for category in default_grade_categories:
        try:
            c.execute("INSERT INTO gradebook_categories (name, description, weight) VALUES (?, ?, ?)", category)
        except sqlite3.IntegrityError:
            pass  # Category already exists

    # Insert default notification settings for different types
    default_notification_settings = [
        ('payment_reminder', 'Payment due date reminders'),
        ('payment_overdue', 'Overdue payment notifications'),
        ('grade_posted', 'New grade posted notifications'),
        ('gpa_update', 'GPA calculation updates'),
        ('attendance_warning', 'Low attendance warnings'),
        ('system_announcement', 'System announcements and updates'),
        ('report_card_ready', 'Report card generation notifications')
    ]

    for setting_type, description in default_notification_settings:
        try:
            # Default settings for all users (user_id is NULL for global defaults)
            c.execute("INSERT INTO notification_settings (user_id, notification_type, in_app_enabled) VALUES (?, ?, ?)",
                     (None, setting_type, 1))
        except sqlite3.IntegrityError:
            pass  # Setting already exists

    # Create images directory if not exists
    if not os.path.exists("images"):
        os.makedirs("images")

    # Create notes directory if not exists
    if not os.path.exists("notes"):
        os.makedirs("notes")

    conn.commit()
    conn.close()

def log_action(user, action, details=""):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO audit_logs (user, action, details) VALUES (?, ?, ?)", (user, action, details))
    conn.commit()
    conn.close()

# ==========================================mins
# 2. APPLICATION CLASS (GUI)
# ==========================================

class ProStudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Student Management System Pro v3.0")
        self.geometry("1300x800")
        self.configure(bg="#e8f5e8")  # Changed to light green background
        
        # Initialize DB
        init_database()
        
        # App State
        self.current_user = None
        self.user_role = None
        self.theme = "light"
        
        # Styles
        self.style = ttk.Style()
        self.setup_styles()
        
        # Login Screen
        self.withdraw()
        self.login_window()

    def setup_styles(self):
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#e8f5e8")  # Changed to light green
        self.style.configure("TButton", padding=6, font=('Segoe UI', 9))
        self.style.configure("Treeview", rowheight=25, font=('Segoe UI', 9))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        self.style.configure("Sidebar.TButton", padding=10, anchor='w')
        self.style.configure("Card.TFrame", background="white")

    def hash_pass(self, pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()

    # ----------------------
    # SECURITY & AUTH
    # ----------------------
    def login_window(self):
        self.login_win = tk.Toplevel(self)
        self.login_win.title("System Login")
        self.login_win.geometry("400x350")  # Increased height for animation
        self.login_win.configure(bg="white")
        self.login_win.resizable(False, False)
        
        # Center the window manually
        self.login_win.update_idletasks()
        x = (self.login_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.login_win.winfo_screenheight() // 2) - (350 // 2)
        self.login_win.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(self.login_win, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)
        
        # Animated Welcome Message
        self.welcome_label = ttk.Label(frame, text="", font=('Segoe UI', 16, 'bold'), foreground="#2e7d32")
        self.welcome_label.pack(pady=10)
        self.animate_welcome_text("Welcome to Ultimate Student Management System Pro v3.0")
        
        # Variables
        self.uname_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        
        ttk.Label(frame, text="Username").pack(anchor='w', pady=(20,5))
        ttk.Entry(frame, textvariable=self.uname_var).pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Password").pack(anchor='w', pady=5)
        ttk.Entry(frame, textvariable=self.pass_var, show="*").pack(fill=tk.X, pady=5)
        
        ttk.Button(frame, text="Login", command=self.authenticate).pack(pady=20)
        
        self.login_win.protocol("WM_DELETE_WINDOW", self.on_close_main)

    def animate_welcome_text(self, full_text):
        self.welcome_text = ""
        self.full_welcome_text = full_text
        self.animate_index = 0
        self.animate_text()

    def animate_text(self):
        if self.animate_index < len(self.full_welcome_text):
            self.welcome_text += self.full_welcome_text[self.animate_index]
            self.welcome_label.config(text=self.welcome_text)
            self.animate_index += 1
            self.login_win.after(100, self.animate_text)  # 100ms delay for typing effect
        else:
            # After full text, wait 2 seconds then restart
            self.login_win.after(2000, self.restart_login_animation)

    def restart_login_animation(self):
        self.welcome_text = ""
        self.animate_index = 0
        self.animate_text()

    def animate_dashboard_welcome(self):
        welcome_text = f"Welcome back, {self.current_user}! Ready to manage your students?"
        self.dashboard_welcome_text = ""
        self.dashboard_full_text = welcome_text
        self.dashboard_index = 0
        self.animate_dashboard_text()

    def animate_dashboard_text(self):
        if self.dashboard_index < len(self.dashboard_full_text):
            self.dashboard_welcome_text += self.dashboard_full_text[self.dashboard_index]
            self.dashboard_welcome_label.config(text=self.dashboard_welcome_text)
            self.dashboard_index += 1
            self.after(100, self.animate_dashboard_text)
        else:
            # After full text, wait 3 seconds then restart
            self.after(3000, self.restart_dashboard_animation)

    def restart_dashboard_animation(self):
        self.dashboard_welcome_text = ""
        self.dashboard_index = 0
        self.animate_dashboard_text()

    def authenticate(self):
        u = self.uname_var.get()
        p = self.pass_var.get()
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (u,))
        user = c.fetchone()
        
        if user and user['password'] == self.hash_pass(p):
            self.current_user = user['username']
            self.user_role = user['role']
            self.current_user_id = user['id']
            
            # Update last login
            c.execute("UPDATE users SET last_login=? WHERE username=?", (datetime.datetime.now(), u))
            conn.commit()
            conn.close()
            
            log_action(self.current_user, "LOGIN", "Successful login")
            
            self.login_win.destroy()
            self.deiconify()
            self.setup_main_ui()
        else:
            log_action("Unknown", "LOGIN_FAILED", f"Attempted user: {u}")
            messagebox.showerror("Error", "Invalid Credentials")

    # ----------------------
    # MAIN UI LAYOUT
    # ----------------------
    def setup_main_ui(self):
        # Main Container
        self.main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, width=200)
        self.setup_sidebar()
        self.main_container.add(self.sidebar, weight=0)

        # Main Area
        self.main_area = ttk.Frame(self.main_container)
        self.main_container.add(self.main_area, weight=1)
        
        # Dashboard Default
        self.show_dashboard()

    def setup_sidebar(self):
        # Header
        ttk.Label(self.sidebar, text=f"Welcome,\n{self.current_user}", font=('Segoe UI', 10)).pack(pady=20, anchor='w', padx=10)
        
        # Buttons - Different menus based on role
        self.notification_btn = None
        
        if self.user_role == 'parent':
            # Parent Portal Menu
            btns = [
                ("🏠 Parent Dashboard", self.show_parent_dashboard),
                ("👨‍👩‍👧‍👦 My Children", self.show_parent_children),
                ("📊 Academic Progress", self.show_parent_grades),
                ("💰 Payment Status", self.show_parent_payments),
                ("📅 Attendance", self.show_parent_attendance),
                ("📄 Report Cards", self.show_parent_reports),
                ("🔔 Notifications", self.show_parent_notifications),
                ("💬 Messages", self.show_parent_messages),
                ("⚙️ Settings", self.show_parent_settings),
            ]
        else:
            # Admin/User Menu
            btns = [
                ("📊 Dashboard", self.show_dashboard),
                ("👥 Students", self.show_students),
                ("💰 Payment Tracking", self.show_payments),
                ("📓 Gradebook", self.show_gradebook),
                ("🔔 Notifications", self.show_notifications),
                ("📚 Subjects & Marks", self.show_subjects),
                ("🎥 Tutorials", self.show_tutorials),
                ("📄 Study Notes", self.show_study_notes),
                ("📅 Attendance", self.show_attendance),
                ("📈 Analytics", self.show_analytics),
                ("⚙️ Settings", self.show_settings),
                ("👥 User Management", self.show_user_mgmt) if self.user_role == 'admin' else None,
                ("📄 Logs", self.show_logs) if self.user_role == 'admin' else None,
            ]
        
        for txt, cmd in btns:
            if txt:
                btn = ttk.Button(self.sidebar, text=txt, style="Sidebar.TButton", command=cmd)
                btn.pack(fill=tk.X, padx=5, pady=2)
                if "Notifications" in txt:
                    self.notification_btn = btn

        # Update notification badge
        self.update_notification_badge()

        # Theme Toggle
        ttk.Button(self.sidebar, text="🌓 Toggle Theme", command=self.toggle_theme).pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
        ttk.Button(self.sidebar, text="🚪 Logout", command=self.logout).pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def update_notification_badge(self):
        """Update the notification button with unread count"""
        if self.notification_btn:
            try:
                unread_count = self.get_unread_notification_count()
                if unread_count > 0:
                    self.notification_btn.config(text=f"🔔 Notifications ({unread_count})")
                else:
                    self.notification_btn.config(text="🔔 Notifications")
            except:
                self.notification_btn.config(text="🔔 Notifications")

    def get_unread_notification_count(self):
        """Get count of unread notifications for current user"""
        conn = get_db_connection()
        try:
            if self.user_role == 'admin':
                count = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0 AND is_active = 1').fetchone()[0]
            else:
                count = conn.execute('''
                    SELECT COUNT(*) FROM notification_recipients nr
                    JOIN notifications n ON nr.notification_id = n.id
                    WHERE nr.recipient_id = ? AND nr.is_read = 0 AND n.is_active = 1
                ''', (self.current_user,)).fetchone()[0]
            return count
        except:
            return 0
        finally:
            conn.close()

    # ----------------------
    # DASHBOARD
    # ----------------------
    def show_dashboard(self):
        self.clear_main_area()
        
        # Animated Welcome Message
        welcome_frame = ttk.Frame(self.main_area)
        welcome_frame.pack(fill=tk.X, padx=20, pady=10)
        self.dashboard_welcome_label = ttk.Label(welcome_frame, text="", font=('Segoe UI', 14, 'bold'), foreground="#2e7d32")
        self.dashboard_welcome_label.pack()
        self.animate_dashboard_welcome()
        
        # Header
        header = ttk.Frame(self.main_area)
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="Dashboard Overview", font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header, text=datetime.datetime.now().strftime("%A, %d %B %Y"), font=('Segoe UI', 10)).pack(side=tk.RIGHT)

        # Stats Cards
        stats_frame = ttk.Frame(self.main_area)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.create_stat_card(stats_frame, "Total Students", self.get_count("students"), "#3498db")
        self.create_stat_card(stats_frame, "Total Subjects", self.get_count("subjects"), "#2ecc71")
        self.create_stat_card(stats_frame, "Male/Female", self.get_gender_ratio(), "#9b59b6")
        self.create_stat_card(stats_frame, "Average Score", f"{self.get_avg_marks():.1f}%", "#e74c3c")

        # Recent Activity
        activity_frame = ttk.LabelFrame(self.main_area, text="Recent System Logs", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        logs = self.get_recent_logs(10)
        cols = ["Time", "User", "Action"]
        tree = ttk.Treeview(activity_frame, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True)
        
        for log in logs:
            tree.insert("", tk.END, values=(log['timestamp'], log['user'], log['action']))

    def create_stat_card(self, parent, title, value, color):
        f = tk.Frame(parent, bg=color, padx=20, pady=20)
        f.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        tk.Label(f, text=title, bg=color, fg="white", font=('Segoe UI', 9)).pack(anchor='w')
        tk.Label(f, text=value, bg=color, fg="white", font=('Segoe UI', 16, 'bold')).pack(anchor='w')

    def get_count(self, table):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {table}")
        r = c.fetchone()[0]
        conn.close()
        return r

    def get_gender_ratio(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT gender, COUNT(*) as cnt FROM students GROUP BY gender")
        res = c.fetchall()
        conn.close()
        m = next((r['cnt'] for r in res if r['gender'] == 'Male'), 0)
        f = next((r['cnt'] for r in res if r['gender'] == 'Female'), 0)
        return f"{m}/{f}"

    def get_avg_marks(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT AVG(marks) FROM subjects")
        r = c.fetchone()[0]
        conn.close()
        return r if r else 0

    def get_recent_logs(self, limit):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        res = c.fetchall()
        conn.close()
        return res

    # ----------------------
    # STUDENT MANAGEMENT
    # ----------------------
    def show_students(self):
        self.clear_main_area()
        
        # Toolbar
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="➕ Add Student", command=self.add_student_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="🗑️ Delete Selected", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="📝 Edit Selected", command=self.edit_student_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="👁️ View Photo", command=self.view_student_photo).pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(tb, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_students)
        ttk.Entry(tb, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        # Data Import / Export
        ttk.Button(tb, text="⬆️ Import CSV", command=self.import_students_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tb, text="⬇️ Export CSV", command=self.export_students_csv).pack(side=tk.RIGHT)
        
        self.student_search_query = ""
        
        # Treeview
        cols = ["ID", "Student ID", "Name", "Email", "Program", "Gender", "Status", "GPA"]
        self.tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        
        # Sorting Logic
        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self.treeview_sort_column(self.tree, _c, False))
            self.tree.column(c, width=100, anchor='center')
        self.tree.column("Name", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pagination
        pg_frame = ttk.Frame(self.main_area)
        pg_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(pg_frame, text="< Prev", command=lambda: self.load_students_page(-1)).pack(side=tk.LEFT)
        self.page_label = ttk.Label(pg_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(pg_frame, text="Next >", command=lambda: self.load_students_page(1)).pack(side=tk.RIGHT)
        
        self.current_page = 0
        self.load_students_page(0)

    def load_students_page(self, direction):
        self.current_page += direction
        if self.current_page < 0:
            self.current_page = 0
        
        limit = 50
        offset = self.current_page * limit
        
        conn = get_db_connection()
        c = conn.cursor()
        query_sql = '''
            SELECT s.id, s.student_id, s.name, s.email, s.program, s.gender, s.status,
                   (SELECT AVG(sub.marks) FROM subjects sub WHERE sub.student_id = s.student_id) as gpa
            FROM students s
        '''
        params = []
        if self.student_search_query:
            search_term = f"%{self.student_search_query}%"
            query_sql += '''
                WHERE lower(s.student_id) LIKE ? OR lower(s.name) LIKE ? OR lower(s.email) LIKE ? OR lower(s.program) LIKE ?
            '''
            params.extend([search_term] * 4)

        query_sql += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        c.execute(query_sql, params)

        rows = c.fetchall()
        if not rows and direction > 0:
            self.current_page -= 1
            conn.close()
            return

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            gpa = f"{r['gpa']:.2f}" if r['gpa'] is not None else "N/A"
            self.tree.insert("", tk.END, values=(r['id'], r['student_id'], r['name'], r['email'], r['program'], r['gender'], r['status'], gpa))

        conn.close()
        self.page_label.config(text=f"Page {self.current_page + 1}")

    def filter_students(self, *args):
        self.student_search_query = self.search_var.get().strip().lower()
        self.current_page = 0
        self.load_students_page(0)

    def import_students_csv(self):
        path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        required_fields = ['student_id', 'name']
        inserted = 0
        skipped = 0
        errors = []

        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = [h.strip().lower() for h in reader.fieldnames or []]
            for field in required_fields:
                if field not in headers:
                    messagebox.showerror("Import Error", f"CSV must contain '{field}' column.")
                    return

            conn = get_db_connection()
            c = conn.cursor()
            for row_number, row in enumerate(reader, start=2):
                sid = row.get('student_id', '').strip()
                name = row.get('name', '').strip()
                if not sid or not name:
                    skipped += 1
                    continue

                email = row.get('email', '').strip()
                phone = row.get('phone', '').strip()
                gender = row.get('gender', '').strip()
                dob = row.get('dob', '').strip()
                address = row.get('address', '').strip()
                program = row.get('program', '').strip()
                guardian_name = row.get('guardian_name', '').strip()
                guardian_phone = row.get('guardian_phone', '').strip()
                status = row.get('status', 'Active').strip() or 'Active'

                try:
                    c.execute('''INSERT INTO students (student_id, name, email, phone, gender, dob, address, program, guardian_name, guardian_phone, status)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (sid, name, email, phone, gender, dob, address, program, guardian_name, guardian_phone, status))
                    inserted += 1
                except sqlite3.IntegrityError:
                    skipped += 1
                except Exception as e:
                    errors.append(f"Line {row_number}: {str(e)}")

            conn.commit()
            conn.close()

        summary = f"Imported {inserted} students. Skipped {skipped} rows."
        if errors:
            summary += f"\nErrors:\n{chr(10).join(errors[:5])}"
        messagebox.showinfo("Import Complete", summary)
        log_action(self.current_user, "IMPORT_STUDENTS", f"Imported {inserted} rows from {os.path.basename(path)}")
        self.load_students_page(0)

    def safe_copy_file(self, source_path, dest_folder, prefix):
        if not source_path or not os.path.exists(source_path):
            return None
        ext = os.path.splitext(source_path)[1]
        timestamp = int(datetime.datetime.now().timestamp())
        safe_name = f"{prefix}_{timestamp}{ext}"
        dest_path = os.path.join(dest_folder, safe_name)
        os.makedirs(dest_folder, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        return dest_path

    def add_student_dialog(self):
        self.input_win = tk.Toplevel(self)
        self.input_win.title("Add New Student")
        self.input_win.geometry("500x650")
        self.input_win.transient(self)
        self.input_win.grab_set()
        
        # Fields
        fields = [
            ("Student ID", "student_id"), ("Full Name", "name"), ("Email", "email"),
            ("Phone", "phone"), ("Gender", "gender"), ("Date of Birth (YYYY-MM-DD)", "dob"),
            ("Address", "address"), ("Program", "program"), ("Guardian Name", "guardian_name"),
            ("Guardian Phone", "guardian_phone")
        ]
        
        self.entries = {}
        f = ttk.Frame(self.input_win, padding=20)
        f.pack(fill=tk.BOTH, expand=True)
        
        for i, (lbl, key) in enumerate(fields):
            ttk.Label(f, text=lbl).grid(row=i, column=0, sticky='w', pady=5)
            if key == "gender":
                cb = ttk.Combobox(f, values=["Male", "Female", "Other"])
                cb.grid(row=i, column=1, sticky='ew', pady=5)
                self.entries[key] = cb
            else:
                e = ttk.Entry(f)
                e.grid(row=i, column=1, sticky='ew', pady=5)
                self.entries[key] = e
        
        # Image Upload Section (Admin only)
        if self.user_role == 'admin':
            ttk.Label(f, text="Student Photo:").grid(row=len(fields), column=0, sticky='w', pady=5)
            img_frame = ttk.Frame(f)
            img_frame.grid(row=len(fields), column=1, sticky='ew', pady=5)
            self.image_path_var = tk.StringVar()
            ttk.Entry(img_frame, textvariable=self.image_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(img_frame, text="Browse", command=self.select_image).pack(side=tk.RIGHT, padx=(5,0))
            save_row = len(fields) + 1
        else:
            self.image_path_var = tk.StringVar()  # Still create for save logic
            save_row = len(fields)
        
        ttk.Button(f, text="Save", command=self.save_student).grid(row=save_row, column=1, pady=20)
        
        # Auto-ID Generation
        self.entries['student_id'].insert(0, self.generate_student_id())
        self.is_edit = False  # Flag to indicate add mode

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            self.image_path_var.set(file_path)

    def generate_student_id(self):
        year = datetime.datetime.now().year
        rand = random.randint(1000, 9999)
        return f"STU-{year}-{rand}"

    def save_student(self):
        data = {k: (e.get() if hasattr(e, 'get') else e.get()) for k, e in self.entries.items()}
        
        # Handle image
        image_path = None
        selected_image = self.image_path_var.get()
        if selected_image:
            image_path = self.safe_copy_file(selected_image, "images", data['student_id'])
        
        # Validation
        if not data['name'] or not data['student_id']:
            messagebox.showwarning("Validation Error", "Name and ID are required.")
            return
        
        # Check if editing
        if hasattr(self, 'is_edit') and self.is_edit:
            # Update existing student
            conn = get_db_connection()
            c = conn.cursor()
            try:
                c.execute('''UPDATE students SET name=?, email=?, phone=?, gender=?, dob=?, address=?, program=?, guardian_name=?, guardian_phone=?, image_path=?
                            WHERE student_id=?''',
                          (data['name'], data['email'], data['phone'], data['gender'], data['dob'],
                           data['address'], data['program'], data['guardian_name'], data['guardian_phone'], image_path, data['student_id']))
                conn.commit()
                conn.close()
                log_action(self.current_user, "EDIT_STUDENT", f"Edited {data['name']}")
                messagebox.showinfo("Success", "Student Updated Successfully!")
                self.input_win.destroy()
                self.load_students_page(0)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                conn.close()
        else:
            # Insert new student
            conn = get_db_connection()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO students (student_id, name, email, phone, gender, dob, address, program, guardian_name, guardian_phone, status, image_path)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (data['student_id'], data['name'], data['email'], data['phone'], data['gender'], 
                           data['dob'], data['address'], data['program'], data['guardian_name'], data['guardian_phone'], 'Active', image_path))
                conn.commit()
                conn.close()
                log_action(self.current_user, "ADD_STUDENT", f"Added {data['name']}")
                messagebox.showinfo("Success", "Student Added Successfully!")
                self.input_win.destroy()
                self.load_students_page(0)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Student ID already exists!")
                conn.close()

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Confirm", f"Delete {len(selected)} selected student(s)?"):
            for item in selected:
                student_id = self.tree.item(item)['values'][1]  # Student ID column
                conn = get_db_connection()
                c = conn.cursor()
                # Cascade delete
                c.execute("DELETE FROM subjects WHERE student_id=?", (student_id,))
                c.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
                c.execute("DELETE FROM students WHERE student_id=?", (student_id,))
                conn.commit()
                conn.close()
            log_action(self.current_user, "DELETE_STUDENT", f"Deleted {len(selected)} students")
            self.load_students_page(0)

    def edit_student_dialog(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        student_id = self.tree.item(selected[0])['values'][1]
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        data = c.fetchone()
        conn.close()
        
        if not data:
            return
        
        # Reuse Add Dialog but fill data
        self.add_student_dialog()
        self.input_win.title("Edit Student")
        self.is_edit = True
        
        # Fill data
        self.entries['student_id'].delete(0, tk.END)
        self.entries['student_id'].insert(0, data['student_id'])
        self.entries['student_id'].config(state='disabled')
        
        self.entries['name'].delete(0, tk.END)
        self.entries['name'].insert(0, data['name'])
        
        self.entries['email'].delete(0, tk.END)
        self.entries['email'].insert(0, data['email'] if data['email'] else "")
        
        self.entries['phone'].delete(0, tk.END)
        self.entries['phone'].insert(0, data['phone'] if data['phone'] else "")
        
        self.entries['gender'].set(data['gender'] if data['gender'] else "")
        
        self.entries['dob'].delete(0, tk.END)
        self.entries['dob'].insert(0, data['dob'] if data['dob'] else "")
        
        self.entries['address'].delete(0, tk.END)
        self.entries['address'].insert(0, data['address'] if data['address'] else "")
        
        self.entries['program'].delete(0, tk.END)
        self.entries['program'].insert(0, data['program'] if data['program'] else "")
        
        self.entries['guardian_name'].delete(0, tk.END)
        self.entries['guardian_name'].insert(0, data['guardian_name'] if data['guardian_name'] else "")
        
        self.entries['guardian_phone'].delete(0, tk.END)
        self.entries['guardian_phone'].insert(0, data['guardian_phone'] if data['guardian_phone'] else "")
        
        # Load existing image
        if data['image_path']:
            self.image_path_var.set(data['image_path'])

    def view_student_photo(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student first.")
            return
        
        student_id = self.tree.item(selected[0])['values'][1]
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT image_path FROM students WHERE student_id=?", (student_id,))
        row = c.fetchone()
        conn.close()
        
        if row and row['image_path'] and os.path.exists(row['image_path']):
            os.startfile(row['image_path'])
        else:
            messagebox.showinfo("No Photo", "No photo available for this student.")

    # ----------------------
    # PAYMENT TRACKING
    # ----------------------
    def show_payments(self):
        self.clear_main_area()

        # Toolbar
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="💰 Record Payment", command=self.record_payment_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="➕ Add Payment Category", command=self.add_payment_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="🗑️ Delete Selected", command=self.delete_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="📝 Edit Selected", command=self.edit_payment_dialog).pack(side=tk.LEFT, padx=5)

        # Filters
        filter_frame = ttk.Frame(tb)
        filter_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT)
        self.payment_status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.payment_status_var,
                                   values=["All", "Pending", "Paid", "Overdue", "Cancelled"], width=10)
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.load_payments())

        ttk.Label(filter_frame, text="Student:").pack(side=tk.LEFT, padx=(10, 0))
        self.payment_student_var = tk.StringVar(value="All")
        self.student_combo = ttk.Combobox(filter_frame, textvariable=self.payment_student_var, width=20)
        self.student_combo.pack(side=tk.LEFT, padx=5)
        self.student_combo.bind('<<ComboboxSelected>>', lambda e: self.load_payments())

        # Search
        ttk.Label(tb, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.payment_search_var = tk.StringVar()
        self.payment_search_var.trace('w', self.filter_payments)
        ttk.Entry(tb, textvariable=self.payment_search_var, width=25).pack(side=tk.LEFT)

        # Export
        ttk.Button(tb, text="⬇️ Export Report", command=self.export_payments_report).pack(side=tk.RIGHT)

        # Treeview
        cols = ["ID", "Student ID", "Student Name", "Category", "Amount", "Status", "Due Date", "Payment Date", "Method"]
        self.payment_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")

        for c in cols:
            self.payment_tree.heading(c, text=c, command=lambda _c=c: self.treeview_sort_column(self.payment_tree, _c, False))
            if c in ["Amount"]:
                self.payment_tree.column(c, width=100, anchor='e')
            elif c in ["Student Name", "Category"]:
                self.payment_tree.column(c, width=150)
            else:
                self.payment_tree.column(c, width=100, anchor='center')

        self.payment_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Summary Panel
        summary_frame = ttk.Frame(self.main_area)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.total_pending_label = ttk.Label(summary_frame, text="Total Pending: $0.00", font=('Segoe UI', 10, 'bold'))
        self.total_pending_label.pack(side=tk.LEFT, padx=20)

        self.total_paid_label = ttk.Label(summary_frame, text="Total Paid: $0.00", font=('Segoe UI', 10, 'bold'))
        self.total_paid_label.pack(side=tk.LEFT, padx=20)

        self.total_overdue_label = ttk.Label(summary_frame, text="Total Overdue: $0.00", font=('Segoe UI', 10, 'bold'), foreground="red")
        self.total_overdue_label.pack(side=tk.LEFT, padx=20)

        # Load data
        self.load_payment_students()
        self.load_payments()
        self.update_payment_summary()

    def load_payment_students(self):
        """Load student list for payment filtering"""
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
        conn.close()

        student_list = ["All"] + [f"{s['student_id']} - {s['name']}" for s in students]
        self.student_combo['values'] = student_list

    def load_payments(self):
        """Load payments with filtering"""
        # Clear existing items
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)

        conn = get_db_connection()
        query = """
            SELECT p.id, p.student_id, s.name as student_name, pc.name as category,
                   p.amount, p.status, p.due_date, p.payment_date, p.payment_method
            FROM payments p
            JOIN students s ON p.student_id = s.student_id
            JOIN payment_categories pc ON p.category_id = pc.id
            WHERE 1=1
        """
        params = []

        # Status filter
        if self.payment_status_var.get() != "All":
            query += " AND p.status = ?"
            params.append(self.payment_status_var.get())

        # Student filter
        if self.payment_student_var.get() != "All":
            student_id = self.payment_student_var.get().split(" - ")[0]
            query += " AND p.student_id = ?"
            params.append(student_id)

        query += " ORDER BY p.created_at DESC"

        payments = conn.execute(query, params).fetchall()
        conn.close()

        for payment in payments:
            # Format amounts and dates
            amount = f"${payment['amount']:.2f}"
            due_date = payment['due_date'] or "N/A"
            payment_date = payment['payment_date'] or "N/A"
            method = payment['payment_method'] or "N/A"

            # Color coding for status
            tags = []
            if payment['status'] == 'Overdue':
                tags.append('overdue')
            elif payment['status'] == 'Paid':
                tags.append('paid')
            elif payment['status'] == 'Pending':
                tags.append('pending')

            self.payment_tree.insert("", tk.END, values=(
                payment['id'], payment['student_id'], payment['student_name'],
                payment['category'], amount, payment['status'], due_date,
                payment_date, method
            ), tags=tags)

        # Configure tags for color coding
        self.payment_tree.tag_configure('overdue', background='#ffebee')
        self.payment_tree.tag_configure('paid', background='#e8f5e8')
        self.payment_tree.tag_configure('pending', background='#fff3e0')

    def filter_payments(self, *args):
        """Filter payments based on search"""
        search_term = self.payment_search_var.get().lower()

        for item in self.payment_tree.get_children():
            values = self.payment_tree.item(item, 'values')
            visible = any(search_term in str(value).lower() for value in values)
            self.payment_tree.item(item, open=visible)  # This doesn't hide, but we can modify visibility logic

        # For now, just reload with current filters
        self.load_payments()

    def update_payment_summary(self):
        """Update payment summary statistics"""
        conn = get_db_connection()

        # Total pending
        pending = conn.execute("SELECT SUM(amount) as total FROM payments WHERE status = 'Pending'").fetchone()
        total_pending = pending['total'] or 0

        # Total paid
        paid = conn.execute("SELECT SUM(amount) as total FROM payments WHERE status = 'Paid'").fetchone()
        total_paid = paid['total'] or 0

        # Total overdue
        overdue = conn.execute("SELECT SUM(amount) as total FROM payments WHERE status = 'Overdue'").fetchone()
        total_overdue = overdue['total'] or 0

        conn.close()

        self.total_pending_label.config(text=f"Total Pending: ${total_pending:.2f}")
        self.total_paid_label.config(text=f"Total Paid: ${total_paid:.2f}")
        self.total_overdue_label.config(text=f"Total Overdue: ${total_overdue:.2f}", foreground="red" if total_overdue > 0 else "black")

    def record_payment_dialog(self):
        """Dialog to record a new payment"""
        dialog = tk.Toplevel(self)
        dialog.title("Record Payment")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # Form fields
        ttk.Label(dialog, text="Student:").pack(pady=5)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(dialog, textvariable=student_var, width=40)
        student_combo.pack(pady=5)

        # Load students
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
        student_list = [f"{s['student_id']} - {s['name']}" for s in students]
        student_combo['values'] = student_list

        ttk.Label(dialog, text="Payment Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, width=40)
        category_combo.pack(pady=5)

        # Load categories
        categories = conn.execute("SELECT name FROM payment_categories WHERE is_active = 1 ORDER BY name").fetchall()
        category_list = [c['name'] for c in categories]
        category_combo['values'] = category_list
        conn.close()

        ttk.Label(dialog, text="Amount ($):").pack(pady=5)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).pack(pady=5)

        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").pack(pady=5)
        due_date_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=due_date_var).pack(pady=5)

        ttk.Label(dialog, text="Payment Date (YYYY-MM-DD):").pack(pady=5)
        payment_date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        ttk.Entry(dialog, textvariable=payment_date_var).pack(pady=5)

        ttk.Label(dialog, text="Payment Method:").pack(pady=5)
        method_var = tk.StringVar()
        method_combo = ttk.Combobox(dialog, textvariable=method_var, values=[
            "Cash", "Bank Transfer", "Zanaco Bank", "Credit Card", "Debit Card", "Mobile Money", "Airtel Money", "Cheque", "Scholarship", "Installment"
        ])
        method_combo.pack(pady=5)

        ttk.Label(dialog, text="Status:").pack(pady=5)
        status_var = tk.StringVar(value="Paid")
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["Pending", "Paid", "Overdue", "Cancelled"])
        status_combo.pack(pady=5)

        ttk.Label(dialog, text="Reference Number:").pack(pady=5)
        ref_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=ref_var).pack(pady=5)

        ttk.Label(dialog, text="Notes:").pack(pady=5)
        notes_text = tk.Text(dialog, height=3, width=40)
        notes_text.pack(pady=5)

        def save_payment():
            if not student_var.get() or not category_var.get() or not amount_var.get():
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            try:
                amount = float(amount_var.get())
                student_id = student_var.get().split(" - ")[0]

                conn = get_db_connection()
                category_id = conn.execute("SELECT id FROM payment_categories WHERE name = ?", (category_var.get(),)).fetchone()['id']

                conn.execute("""
                    INSERT INTO payments (student_id, category_id, amount, payment_date, due_date,
                                       payment_method, status, reference_number, notes, recorded_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_id, category_id, amount, payment_date_var.get(), due_date_var.get(),
                      method_var.get(), status_var.get(), ref_var.get(), notes_text.get("1.0", tk.END).strip(), self.current_user))

                conn.commit()
                conn.close()

                # Generate payment confirmation notification
                title = f"Payment Recorded: ${amount:.2f}"
                message = f"Dear Student,\n\nYour payment of ${amount:.2f} has been successfully recorded.\n\nPayment Method: {method_var.get()}\nReference: {ref_var.get()}\nDate: {payment_date_var.get()}\n\nThank you for your payment!\n\nBest regards,\nFinance Office"

                create_notification(title, message, 'payment', 'normal', 'specific_student', student_id, self.current_user, 30)

                log_action(self.current_user, "Recorded Payment", f"Payment of ${amount} for student {student_id}")
                messagebox.showinfo("Success", "Payment recorded successfully!")
                dialog.destroy()
                self.load_payments()
                self.update_payment_summary()

            except ValueError:
                messagebox.showerror("Error", "Invalid amount format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to record payment: {str(e)}")

        ttk.Button(dialog, text="Save Payment", command=save_payment).pack(pady=20)

    def add_payment_category_dialog(self):
        """Dialog to add a new payment category"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Payment Category")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Category Name:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var).pack(pady=5)

        ttk.Label(dialog, text="Default Amount ($):").pack(pady=10)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).pack(pady=5)

        def save_category():
            if not name_var.get():
                messagebox.showerror("Error", "Category name is required")
                return

            try:
                default_amount = float(amount_var.get()) if amount_var.get() else 0.0

                conn = get_db_connection()
                conn.execute("INSERT INTO payment_categories (name, description, default_amount) VALUES (?, ?, ?)",
                           (name_var.get(), desc_var.get(), default_amount))
                conn.commit()
                conn.close()

                log_action(self.current_user, "Added Payment Category", f"Category: {name_var.get()}")
                messagebox.showinfo("Success", "Payment category added successfully!")
                dialog.destroy()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category name already exists")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format")

        ttk.Button(dialog, text="Save Category", command=save_category).pack(pady=20)

    def delete_payment(self):
        """Delete selected payment"""
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected payment?"):
            item = self.payment_tree.item(selected[0])
            payment_id = item['values'][0]

            conn = get_db_connection()
            conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
            conn.close()

            log_action(self.current_user, "Deleted Payment", f"Payment ID: {payment_id}")
            self.load_payments()
            self.update_payment_summary()

    def edit_payment_dialog(self):
        """Dialog to edit selected payment"""
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to edit")
            return

        item = self.payment_tree.item(selected[0])
        payment_id = item['values'][0]

        conn = get_db_connection()
        payment = conn.execute("""
            SELECT p.*, pc.name as category_name, s.name as student_name
            FROM payments p
            JOIN payment_categories pc ON p.category_id = pc.id
            JOIN students s ON p.student_id = s.student_id
            WHERE p.id = ?
        """, (payment_id,)).fetchone()
        conn.close()

        if not payment:
            messagebox.showerror("Error", "Payment not found")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit Payment")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # Pre-fill form with existing data
        ttk.Label(dialog, text=f"Student: {payment['student_name']} ({payment['student_id']})").pack(pady=10)

        ttk.Label(dialog, text="Payment Category:").pack(pady=5)
        category_var = tk.StringVar(value=payment['category_name'])
        category_combo = ttk.Combobox(dialog, textvariable=category_var, width=40)
        category_combo.pack(pady=5)

        # Load categories
        conn = get_db_connection()
        categories = conn.execute("SELECT name FROM payment_categories WHERE is_active = 1 ORDER BY name").fetchall()
        category_list = [c['name'] for c in categories]
        category_combo['values'] = category_list
        conn.close()

        ttk.Label(dialog, text="Amount ($):").pack(pady=5)
        amount_var = tk.StringVar(value=str(payment['amount']))
        ttk.Entry(dialog, textvariable=amount_var).pack(pady=5)

        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").pack(pady=5)
        due_date_var = tk.StringVar(value=payment['due_date'] or "")
        ttk.Entry(dialog, textvariable=due_date_var).pack(pady=5)

        ttk.Label(dialog, text="Payment Date (YYYY-MM-DD):").pack(pady=5)
        payment_date_var = tk.StringVar(value=payment['payment_date'] or "")
        ttk.Entry(dialog, textvariable=payment_date_var).pack(pady=5)

        ttk.Label(dialog, text="Payment Method:").pack(pady=5)
        method_var = tk.StringVar(value=payment['payment_method'] or "")
        method_combo = ttk.Combobox(dialog, textvariable=method_var, values=[
            "Cash", "Bank Transfer", "Zanaco Bank", "Credit Card", "Debit Card", "Mobile Money", "Airtel Money", "Cheque", "Scholarship", "Installment"
        ])
        method_combo.pack(pady=5)

        ttk.Label(dialog, text="Status:").pack(pady=5)
        status_var = tk.StringVar(value=payment['status'])
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["Pending", "Paid", "Overdue", "Cancelled"])
        status_combo.pack(pady=5)

        ttk.Label(dialog, text="Reference Number:").pack(pady=5)
        ref_var = tk.StringVar(value=payment['reference_number'] or "")
        ttk.Entry(dialog, textvariable=ref_var).pack(pady=5)

        ttk.Label(dialog, text="Notes:").pack(pady=5)
        notes_text = tk.Text(dialog, height=3, width=40)
        notes_text.insert("1.0", payment['notes'] or "")
        notes_text.pack(pady=5)

        def update_payment():
            if not category_var.get() or not amount_var.get():
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            try:
                amount = float(amount_var.get())

                conn = get_db_connection()
                category_id = conn.execute("SELECT id FROM payment_categories WHERE name = ?", (category_var.get(),)).fetchone()['id']

                conn.execute("""
                    UPDATE payments SET
                        category_id = ?, amount = ?, payment_date = ?, due_date = ?,
                        payment_method = ?, status = ?, reference_number = ?, notes = ?
                    WHERE id = ?
                """, (category_id, amount, payment_date_var.get(), due_date_var.get(),
                      method_var.get(), status_var.get(), ref_var.get(),
                      notes_text.get("1.0", tk.END).strip(), payment_id))

                conn.commit()
                conn.close()

                log_action(self.current_user, "Updated Payment", f"Payment ID: {payment_id}")
                messagebox.showinfo("Success", "Payment updated successfully!")
                dialog.destroy()
                self.load_payments()
                self.update_payment_summary()

            except ValueError:
                messagebox.showerror("Error", "Invalid amount format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update payment: {str(e)}")

        ttk.Button(dialog, text="Update Payment", command=update_payment).pack(pady=20)

    def export_payments_report(self):
        """Export payments report to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Payments Report"
            )

            if not filename:
                return

            conn = get_db_connection()
            payments = conn.execute("""
                SELECT p.*, s.name as student_name, pc.name as category_name
                FROM payments p
                JOIN students s ON p.student_id = s.student_id
                JOIN payment_categories pc ON p.category_id = pc.id
                ORDER BY p.created_at DESC
            """).fetchall()
            conn.close()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Student ID', 'Student Name', 'Category', 'Amount',
                            'Status', 'Due Date', 'Payment Date', 'Payment Method',
                            'Reference Number', 'Notes', 'Recorded By', 'Created At']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for payment in payments:
                    writer.writerow({
                        'ID': payment['id'],
                        'Student ID': payment['student_id'],
                        'Student Name': payment['student_name'],
                        'Category': payment['category_name'],
                        'Amount': payment['amount'],
                        'Status': payment['status'],
                        'Due Date': payment['due_date'],
                        'Payment Date': payment['payment_date'],
                        'Payment Method': payment['payment_method'],
                        'Reference Number': payment['reference_number'],
                        'Notes': payment['notes'],
                        'Recorded By': payment['recorded_by'],
                        'Created At': payment['created_at']
                    })

            log_action(self.current_user, "Exported Payments Report", f"File: {filename}")
            messagebox.showinfo("Success", f"Payments report exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    # ----------------------
    # NOTIFICATIONS SYSTEM
    # ----------------------
    def show_notifications(self):
        self.clear_main_area()

        # Header
        header_frame = ttk.Frame(self.main_area)
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(header_frame, text="🔔 Notification Center", font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="➕ Create Notification", command=self.create_notification).pack(side=tk.RIGHT, padx=10)
        ttk.Button(header_frame, text="⚙️ Settings", command=self.notification_settings).pack(side=tk.RIGHT)

        # Main content frame
        content_frame = ttk.Frame(self.main_area)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create notebook for different notification views
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # All Notifications Tab
        all_tab = ttk.Frame(notebook)
        notebook.add(all_tab, text="📋 All Notifications")

        # Unread Notifications Tab
        unread_tab = ttk.Frame(notebook)
        notebook.add(unread_tab, text="🔔 Unread")

        # Create Notification Tab
        create_tab = ttk.Frame(notebook)
        notebook.add(create_tab, text="📝 Create New")

        # Settings Tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="⚙️ Settings")

        # Populate tabs
        self.populate_all_notifications(all_tab)
        self.populate_unread_notifications(unread_tab)
        self.create_notification_form(create_tab)
        self.create_notification_settings(settings_tab)

    def populate_all_notifications(self, parent):
        # Create treeview for notifications
        columns = ('ID', 'Title', 'Type', 'Priority', 'Status', 'Created', 'Expires')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: self.sort_notifications(tree, c))
            tree.column(col, width=100)

        tree.column('Title', width=250)
        tree.column('Created', width=150)
        tree.column('Expires', width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Buttons frame
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="👁️ View", command=lambda: self.view_notification(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Mark as Read", command=lambda: self.mark_as_read(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete", command=lambda: self.delete_notification(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=lambda: self.refresh_notifications(tree)).pack(side=tk.LEFT, padx=5)

        # Load notifications
        self.load_notifications(tree)

        # Bind double-click to view
        tree.bind('<Double-1>', lambda e: self.view_notification(tree))

    def populate_unread_notifications(self, parent):
        # Similar to all notifications but filter for unread
        columns = ('ID', 'Title', 'Type', 'Priority', 'Created', 'Expires')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('Title', width=300)
        tree.column('Created', width=150)
        tree.column('Expires', width=150)

        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="👁️ View", command=lambda: self.view_unread_notification(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Mark as Read", command=lambda: self.mark_unread_as_read(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=lambda: self.refresh_unread_notifications(tree)).pack(side=tk.LEFT, padx=5)

        # Load unread notifications
        self.load_unread_notifications(tree)

        tree.bind('<Double-1>', lambda e: self.view_unread_notification(tree))

    def create_notification_form(self, parent):
        # Form frame
        form_frame = ttk.LabelFrame(parent, text="Create New Notification", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=title_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Message
        ttk.Label(form_frame, text="Message:").grid(row=1, column=0, sticky=tk.W, pady=5)
        message_text = tk.Text(form_frame, height=5, width=50)
        message_text.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Type
        ttk.Label(form_frame, text="Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value="announcement")
        type_combo = ttk.Combobox(form_frame, textvariable=type_var,
                                 values=["announcement", "payment", "grade", "attendance", "system"])
        type_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Priority
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=5)
        priority_var = tk.StringVar(value="normal")
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var,
                                     values=["low", "normal", "high", "urgent"])
        priority_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Recipient Type
        ttk.Label(form_frame, text="Recipient Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        recipient_var = tk.StringVar(value="all")
        recipient_combo = ttk.Combobox(form_frame, textvariable=recipient_var,
                                      values=["all", "student", "admin", "specific_student"])
        recipient_combo.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Specific Student (shown when specific_student is selected)
        student_frame = ttk.Frame(form_frame)
        student_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(student_frame, text="Student:").pack(side=tk.LEFT, padx=5)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(student_frame, textvariable=student_var, width=40)
        student_combo.pack(side=tk.LEFT, padx=5)

        # Initially hide student selection
        student_frame.grid_remove()

        def on_recipient_change(*args):
            if recipient_var.get() == "specific_student":
                student_frame.grid()
                self.load_students_for_combo(student_combo)
            else:
                student_frame.grid_remove()

        recipient_var.trace('w', on_recipient_change)

        # Expires
        ttk.Label(form_frame, text="Expires (days from now):").grid(row=6, column=0, sticky=tk.W, pady=5)
        expires_var = tk.StringVar(value="30")
        ttk.Entry(form_frame, textvariable=expires_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=5)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="📤 Send Notification",
                  command=lambda: self.send_notification(title_var.get(), message_text.get("1.0", tk.END).strip(),
                                                        type_var.get(), priority_var.get(), recipient_var.get(),
                                                        student_var.get() if recipient_var.get() == "specific_student" else None,
                                                        expires_var.get())).pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="🔄 Clear Form",
                  command=lambda: self.clear_notification_form(title_var, message_text, type_var, priority_var,
                                                              recipient_var, student_var, expires_var)).pack(side=tk.LEFT)

    def create_notification_settings(self, parent):
        # Settings frame
        settings_frame = ttk.LabelFrame(parent, text="Notification Preferences", padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Current user settings
        ttk.Label(settings_frame, text=f"Settings for: {self.current_user}", font=('Segoe UI', 12, 'bold')).pack(pady=10)

        # Notification types
        types = [
            ("payment_reminder", "Payment due date reminders"),
            ("payment_overdue", "Overdue payment notifications"),
            ("grade_posted", "New grade posted notifications"),
            ("gpa_update", "GPA calculation updates"),
            ("attendance_warning", "Low attendance warnings"),
            ("system_announcement", "System announcements and updates"),
            ("report_card_ready", "Report card generation notifications")
        ]

        settings_vars = {}

        for notif_type, description in types:
            frame = ttk.Frame(settings_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=f"{description}:").pack(side=tk.LEFT)

            # Get current setting
            current_setting = self.get_notification_setting(self.current_user, notif_type)

            in_app_var = tk.BooleanVar(value=current_setting.get('in_app_enabled', True))
            settings_vars[f"{notif_type}_in_app"] = in_app_var

            ttk.Checkbutton(frame, text="In-App", variable=in_app_var).pack(side=tk.RIGHT, padx=10)

        # Save button
        ttk.Button(settings_frame, text="💾 Save Settings",
                   command=lambda: self.save_notification_settings(settings_vars)).pack(pady=20)

    def load_notifications(self, tree):
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        conn = get_db_connection()
        try:
            # Get notifications based on user role
            if self.user_role == 'admin':
                # Admins see all notifications
                notifications = conn.execute('''
                    SELECT id, title, type, priority,
                           CASE WHEN is_read = 1 THEN 'Read' ELSE 'Unread' END as status,
                           created_at, expires_at
                    FROM notifications
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                ''').fetchall()
            else:
                # Students see notifications sent to them or all
                notifications = conn.execute('''
                    SELECT n.id, n.title, n.type, n.priority,
                           CASE WHEN nr.is_read = 1 THEN 'Read' ELSE 'Unread' END as status,
                           n.created_at, n.expires_at
                    FROM notifications n
                    LEFT JOIN notification_recipients nr ON n.id = nr.notification_id
                        AND nr.recipient_id = ?
                    WHERE n.is_active = 1
                        AND (n.recipient_type = 'all'
                             OR n.recipient_type = 'student'
                             OR (n.recipient_type = 'specific_student' AND n.recipient_id = ?))
                    ORDER BY n.created_at DESC
                ''', (self.current_user, self.current_user)).fetchall()

            for notif in notifications:
                expires = notif[6] or "Never"
                tree.insert('', tk.END, values=(notif[0], notif[1], notif[2], notif[3], notif[4], notif[5], expires))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notifications: {str(e)}")
        finally:
            conn.close()

    def load_unread_notifications(self, tree):
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        conn = get_db_connection()
        try:
            if self.user_role == 'admin':
                notifications = conn.execute('''
                    SELECT id, title, type, priority, created_at, expires_at
                    FROM notifications
                    WHERE is_active = 1 AND is_read = 0
                    ORDER BY created_at DESC
                ''').fetchall()
            else:
                notifications = conn.execute('''
                    SELECT n.id, n.title, n.type, n.priority, n.created_at, n.expires_at
                    FROM notifications n
                    LEFT JOIN notification_recipients nr ON n.id = nr.notification_id
                        AND nr.recipient_id = ?
                    WHERE n.is_active = 1 AND (nr.is_read = 0 OR nr.is_read IS NULL)
                        AND (n.recipient_type = 'all'
                             OR n.recipient_type = 'student'
                             OR (n.recipient_type = 'specific_student' AND n.recipient_id = ?))
                    ORDER BY n.created_at DESC
                ''', (self.current_user, self.current_user)).fetchall()

            for notif in notifications:
                expires = notif[5] or "Never"
                tree.insert('', tk.END, values=(notif[0], notif[1], notif[2], notif[3], notif[4], expires))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load unread notifications: {str(e)}")
        finally:
            conn.close()

    def load_students_for_combo(self, combo):
        conn = get_db_connection()
        try:
            students = conn.execute('SELECT student_id, name FROM students ORDER BY name').fetchall()
            combo['values'] = [f"{s[0]} - {s[1]}" for s in students]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {str(e)}")
        finally:
            conn.close()

    def send_notification(self, title, message, notif_type, priority, recipient_type, student_id=None, expires_days=None):
        if not title or not message:
            messagebox.showerror("Error", "Title and message are required!")
            return

        conn = get_db_connection()
        try:
            # Calculate expiration date
            expires_at = None
            if expires_days and expires_days.isdigit():
                days = int(expires_days)
                expires_at = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

            # Insert notification
            cursor = conn.execute('''
                INSERT INTO notifications (title, message, type, priority, recipient_type, recipient_id, created_by, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, message, notif_type, priority, recipient_type,
                  student_id if recipient_type == 'specific_student' else None,
                  self.current_user, expires_at))

            notification_id = cursor.lastrowid

            # Create recipients based on type
            if recipient_type == 'all':
                # Get all users
                users = conn.execute('SELECT username FROM users').fetchall()
                for user in users:
                    conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                               (notification_id, user[0]))
            elif recipient_type == 'student':
                # Get all students
                students = conn.execute('SELECT student_id FROM students').fetchall()
                for student in students:
                    conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                               (notification_id, student[0]))
            elif recipient_type == 'admin':
                # Get all admins
                admins = conn.execute("SELECT username FROM users WHERE role = 'admin'").fetchall()
                for admin in admins:
                    conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                               (notification_id, admin[0]))
            elif recipient_type == 'specific_student':
                # Specific student
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, student_id))

            conn.commit()
            messagebox.showinfo("Success", "Notification sent successfully!")

            # Clear form (you'll need to implement this)
            # self.clear_notification_form(...)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send notification: {str(e)}")
        finally:
            conn.close()

    def view_notification(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a notification to view!")
            return

        item = tree.item(selected[0])
        notif_id = item['values'][0]

        conn = get_db_connection()
        try:
            notification = conn.execute('SELECT * FROM notifications WHERE id = ?', (notif_id,)).fetchone()
            if notification:
                # Mark as read
                if self.user_role == 'admin':
                    conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notif_id,))
                else:
                    conn.execute('UPDATE notification_recipients SET is_read = 1, read_at = ? WHERE notification_id = ? AND recipient_id = ?',
                               (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notif_id, self.current_user))
                conn.commit()

                # Show notification details
                details = f"Title: {notification[1]}\n\nMessage:\n{notification[2]}\n\nType: {notification[3]}\nPriority: {notification[4]}\nCreated: {notification[8]}\nExpires: {notification[10] or 'Never'}"
                messagebox.showinfo("Notification Details", details)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to view notification: {str(e)}")
        finally:
            conn.close()

    def mark_as_read(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select notifications to mark as read!")
            return

        conn = get_db_connection()
        try:
            for item in selected:
                notif_id = tree.item(item)['values'][0]
                if self.user_role == 'admin':
                    conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notif_id,))
                else:
                    conn.execute('UPDATE notification_recipients SET is_read = 1, read_at = ? WHERE notification_id = ? AND recipient_id = ?',
                               (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notif_id, self.current_user))
            conn.commit()
            messagebox.showinfo("Success", f"Marked {len(selected)} notifications as read!")
            self.refresh_notifications(tree)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark notifications as read: {str(e)}")
        finally:
            conn.close()

    def delete_notification(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select notifications to delete!")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} notification(s)?"):
            conn = get_db_connection()
            try:
                for item in selected:
                    notif_id = tree.item(item)['values'][0]
                    conn.execute('UPDATE notifications SET is_active = 0 WHERE id = ?', (notif_id,))
                conn.commit()
                messagebox.showinfo("Success", f"Deleted {len(selected)} notification(s)!")
                self.refresh_notifications(tree)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete notifications: {str(e)}")
            finally:
                conn.close()

    def get_notification_setting(self, user_id, notif_type):
        conn = get_db_connection()
        try:
            setting = conn.execute('''
                SELECT in_app_enabled, email_enabled, sms_enabled
                FROM notification_settings
                WHERE (user_id = ? OR user_id IS NULL) AND notification_type = ?
                ORDER BY user_id DESC LIMIT 1
            ''', (user_id, notif_type)).fetchone()

            if setting:
                return {
                    'in_app_enabled': bool(setting[0]),
                    'email_enabled': bool(setting[1]),
                    'sms_enabled': bool(setting[2])
                }
            else:
                return {'in_app_enabled': True, 'email_enabled': False, 'sms_enabled': False}

        except Exception as e:
            return {'in_app_enabled': True, 'email_enabled': False, 'sms_enabled': False}
        finally:
            conn.close()

    def save_notification_settings(self, settings_vars):
        conn = get_db_connection()
        try:
            for key, var in settings_vars.items():
                if key.endswith('_in_app'):
                    notif_type = key.replace('_in_app', '')
                    conn.execute('''
                        INSERT OR REPLACE INTO notification_settings
                        (user_id, notification_type, in_app_enabled, updated_at)
                        VALUES (?, ?, ?, ?)
                    ''', (self.current_user, notif_type, var.get(),
                          datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            conn.commit()
            messagebox.showinfo("Success", "Notification settings saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        finally:
            conn.close()

    # Helper methods
    def view_unread_notification(self, tree):
        self.view_notification(tree)
        self.refresh_unread_notifications(tree)

    def mark_unread_as_read(self, tree):
        self.mark_as_read(tree)
        self.refresh_unread_notifications(tree)

    def refresh_notifications(self, tree):
        self.load_notifications(tree)

    def refresh_unread_notifications(self, tree):
        self.load_unread_notifications(tree)

    def create_notification(self):
        # This will open the create tab
        pass

    def notification_settings(self):
        # This will open the settings tab
        pass

    def clear_notification_form(self, title_var, message_text, type_var, priority_var, recipient_var, student_var, expires_var):
        title_var.set("")
        message_text.delete("1.0", tk.END)
        type_var.set("announcement")
        priority_var.set("normal")
        recipient_var.set("all")
        student_var.set("")
        expires_var.set("30")

    def sort_notifications(self, tree, col):
        # Simple sort implementation
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        items.sort()

        for index, (val, item) in enumerate(items):
            tree.move(item, '', index)

    # ----------------------
    # GRADEBOOK & REPORT CARDS
    # ----------------------
    def show_gradebook(self):
        self.clear_main_area()

        # Create notebook for tabs
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Grade Entry Tab
        grade_tab = ttk.Frame(notebook)
        notebook.add(grade_tab, text="📝 Grade Entry")

        # Report Cards Tab
        report_tab = ttk.Frame(notebook)
        notebook.add(report_tab, text="📄 Report Cards")

        # Assessment Setup Tab
        setup_tab = ttk.Frame(notebook)
        notebook.add(setup_tab, text="⚙️ Assessment Setup")

        # Initialize tabs
        self.setup_grade_entry_tab(grade_tab)
        self.setup_report_cards_tab(report_tab)
        self.setup_assessment_tab(setup_tab)

    def setup_grade_entry_tab(self, parent):
        """Setup the grade entry interface"""
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(tb, text="➕ Enter Grades", command=self.enter_grades_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="📊 Calculate GPA", command=self.calculate_student_gpa).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="📈 Grade Analytics", command=self.show_grade_analytics).pack(side=tk.LEFT, padx=5)

        # Filters
        filter_frame = ttk.Frame(tb)
        filter_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(filter_frame, text="Subject:").pack(side=tk.LEFT)
        self.subject_filter_var = tk.StringVar(value="All")
        self.subject_combo = ttk.Combobox(filter_frame, textvariable=self.subject_filter_var, width=20)
        self.subject_combo.pack(side=tk.LEFT, padx=5)
        self.subject_combo.bind('<<ComboboxSelected>>', lambda e: self.load_grades())

        ttk.Label(filter_frame, text="Student:").pack(side=tk.LEFT, padx=(10, 0))
        self.grade_student_var = tk.StringVar(value="All")
        self.grade_student_combo = ttk.Combobox(filter_frame, textvariable=self.grade_student_var, width=20)
        self.grade_student_combo.pack(side=tk.LEFT, padx=5)
        self.grade_student_combo.bind('<<ComboboxSelected>>', lambda e: self.load_grades())

        # Treeview
        cols = ["Student ID", "Student Name", "Subject", "Assessment", "Score", "Max Score", "Grade", "Date"]
        self.grade_tree = ttk.Treeview(parent, columns=cols, show="headings")

        for c in cols:
            self.grade_tree.heading(c, text=c, command=lambda _c=c: self.treeview_sort_column(self.grade_tree, _c, False))
            if c in ["Score", "Max Score"]:
                self.grade_tree.column(c, width=80, anchor='center')
            elif c in ["Student Name", "Subject"]:
                self.grade_tree.column(c, width=150)
            else:
                self.grade_tree.column(c, width=100, anchor='center')

        self.grade_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Load data
        self.load_subjects_filter()
        self.load_students_filter()
        self.load_grades()

    def setup_report_cards_tab(self, parent):
        """Setup the report cards interface"""
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(tb, text="📄 Generate Report Card", command=self.generate_report_card_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="👁️ View Report Card", command=self.view_report_card).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="🖨️ Print Report Card", command=self.print_report_card).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="📊 Academic Summary", command=self.show_academic_summary).pack(side=tk.LEFT, padx=5)

        # Filters
        filter_frame = ttk.Frame(tb)
        filter_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(filter_frame, text="Academic Year:").pack(side=tk.LEFT)
        self.year_filter_var = tk.StringVar(value="All")
        self.year_combo = ttk.Combobox(filter_frame, textvariable=self.year_filter_var, width=15)
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_report_cards())

        ttk.Label(filter_frame, text="Semester:").pack(side=tk.LEFT, padx=(10, 0))
        self.semester_filter_var = tk.StringVar(value="All")
        semester_combo = ttk.Combobox(filter_frame, textvariable=self.semester_filter_var,
                                    values=["All", "Semester 1", "Semester 2", "Annual"], width=12)
        semester_combo.pack(side=tk.LEFT, padx=5)
        semester_combo.bind('<<ComboboxSelected>>', lambda e: self.load_report_cards())

        # Treeview
        cols = ["Student ID", "Student Name", "Academic Year", "Semester", "GPA", "Status", "Generated"]
        self.report_tree = ttk.Treeview(parent, columns=cols, show="headings")

        for c in cols:
            self.report_tree.heading(c, text=c, command=lambda _c=c: self.treeview_sort_column(self.report_tree, _c, False))
            if c == "GPA":
                self.report_tree.column(c, width=80, anchor='center')
            elif c == "Student Name":
                self.report_tree.column(c, width=150)
            else:
                self.report_tree.column(c, width=100, anchor='center')

        self.report_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Load data
        self.load_academic_years()
        self.load_report_cards()

    def setup_assessment_tab(self, parent):
        """Setup the assessment configuration interface"""
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(tb, text="➕ Add Assessment", command=self.add_assessment_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="📂 Add Category", command=self.add_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(tb, text="📅 Academic Year", command=self.manage_academic_year_dialog).pack(side=tk.LEFT, padx=5)

        # Treeview for assessments
        cols = ["Category", "Assessment", "Max Score", "Weight", "Subject", "Date"]
        self.assessment_tree = ttk.Treeview(parent, columns=cols, show="headings")

        for c in cols:
            self.assessment_tree.heading(c, text=c, command=lambda _c=c: self.treeview_sort_column(self.assessment_tree, _c, False))
            if c in ["Max Score", "Weight"]:
                self.assessment_tree.column(c, width=80, anchor='center')
            elif c == "Assessment":
                self.assessment_tree.column(c, width=150)
            else:
                self.assessment_tree.column(c, width=100, anchor='center')

        self.assessment_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.load_assessments()

    def load_subjects_filter(self):
        """Load subjects for filtering"""
        conn = get_db_connection()
        subjects = conn.execute("SELECT DISTINCT subject_name FROM gradebook_categories WHERE subject_name IS NOT NULL ORDER BY subject_name").fetchall()
        conn.close()

        subject_list = ["All"] + [s['subject_name'] for s in subjects if s['subject_name']]
        self.subject_combo['values'] = subject_list

    def load_students_filter(self):
        """Load students for filtering"""
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
        conn.close()

        student_list = ["All"] + [f"{s['student_id']} - {s['name']}" for s in students]
        self.grade_student_combo['values'] = student_list

    def load_academic_years(self):
        """Load academic years for filtering"""
        conn = get_db_connection()
        years = conn.execute("SELECT year_name FROM academic_years ORDER BY start_date DESC").fetchall()
        conn.close()

        year_list = ["All"] + [y['year_name'] for y in years]
        self.year_combo['values'] = year_list

    def load_grades(self):
        """Load grades with filtering"""
        for item in self.grade_tree.get_children():
            self.grade_tree.delete(item)

        conn = get_db_connection()
        query = """
            SELECT gg.id, gg.student_id, s.name as student_name, ga.assessment_name,
                   gg.score, ga.max_score, gg.grade_letter, gg.recorded_at,
                   gc.subject_name
            FROM gradebook_grades gg
            JOIN students s ON gg.student_id = s.student_id
            JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
            JOIN gradebook_categories gc ON ga.category_id = gc.id
            WHERE 1=1
        """
        params = []

        # Subject filter
        if self.subject_filter_var.get() != "All":
            query += " AND gc.subject_name = ?"
            params.append(self.subject_filter_var.get())

        # Student filter
        if self.grade_student_var.get() != "All":
            student_id = self.grade_student_var.get().split(" - ")[0]
            query += " AND gg.student_id = ?"
            params.append(student_id)

        query += " ORDER BY gg.recorded_at DESC"

        grades = conn.execute(query, params).fetchall()
        conn.close()

        for grade in grades:
            score_display = f"{grade['score']:.1f}" if grade['score'] else "N/A"
            max_score = f"{grade['max_score']:.1f}"
            date_display = grade['recorded_at'][:10] if grade['recorded_at'] else "N/A"

            self.grade_tree.insert("", tk.END, values=(
                grade['student_id'], grade['student_name'], grade['subject_name'] or "General",
                grade['assessment_name'], score_display, max_score,
                grade['grade_letter'] or "N/A", date_display
            ))

    def load_report_cards(self):
        """Load report cards with filtering"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        conn = get_db_connection()
        query = """
            SELECT rc.id, rc.student_id, s.name as student_name, ay.year_name,
                   rc.semester, rc.gpa, rc.status, rc.generated_at
            FROM report_cards rc
            JOIN students s ON rc.student_id = s.student_id
            JOIN academic_years ay ON rc.academic_year_id = ay.id
            WHERE 1=1
        """
        params = []

        # Year filter
        if self.year_filter_var.get() != "All":
            query += " AND ay.year_name = ?"
            params.append(self.year_filter_var.get())

        # Semester filter
        if self.semester_filter_var.get() != "All":
            query += " AND rc.semester = ?"
            params.append(self.semester_filter_var.get())

        query += " ORDER BY rc.generated_at DESC"

        report_cards = conn.execute(query, params).fetchall()
        conn.close()

        for rc in report_cards:
            gpa_display = f"{rc['gpa']:.2f}" if rc['gpa'] else "N/A"
            date_display = rc['generated_at'][:10] if rc['generated_at'] else "N/A"

            self.report_tree.insert("", tk.END, values=(
                rc['student_id'], rc['student_name'], rc['year_name'],
                rc['semester'], gpa_display, rc['status'], date_display
            ))

    def load_assessments(self):
        """Load assessments configuration"""
        for item in self.assessment_tree.get_children():
            self.assessment_tree.delete(item)

        conn = get_db_connection()
        assessments = conn.execute("""
            SELECT ga.assessment_name, gc.name as category_name, ga.max_score,
                   ga.weight, gc.subject_name, ga.assessment_date
            FROM gradebook_assessments ga
            JOIN gradebook_categories gc ON ga.category_id = gc.id
            WHERE ga.is_active = 1
            ORDER BY gc.subject_name, ga.assessment_date
        """).fetchall()
        conn.close()

        for assessment in assessments:
            date_display = assessment['assessment_date'] or "N/A"
            subject_display = assessment['subject_name'] or "General"

            self.assessment_tree.insert("", tk.END, values=(
                assessment['category_name'], assessment['assessment_name'],
                f"{assessment['max_score']:.1f}", f"{assessment['weight']:.2f}",
                subject_display, date_display
            ))

    def enter_grades_dialog(self):
        """Dialog to enter grades for assessments"""
        dialog = tk.Toplevel(self)
        dialog.title("Enter Grades")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()

        # Assessment selection
        ttk.Label(dialog, text="Select Assessment:").pack(pady=10)
        assessment_var = tk.StringVar()
        assessment_combo = ttk.Combobox(dialog, textvariable=assessment_var, width=50)
        assessment_combo.pack(pady=5)

        # Load assessments
        conn = get_db_connection()
        assessments = conn.execute("""
            SELECT ga.id, ga.assessment_name, gc.name as category_name, gc.subject_name
            FROM gradebook_assessments ga
            JOIN gradebook_categories gc ON ga.category_id = gc.id
            WHERE ga.is_active = 1
            ORDER BY gc.subject_name, ga.assessment_name
        """).fetchall()
        conn.close()

        assessment_list = [f"{a['subject_name'] or 'General'} - {a['category_name']} - {a['assessment_name']}" for a in assessments]
        assessment_combo['values'] = assessment_list

        # Student grades frame
        grades_frame = ttk.Frame(dialog)
        grades_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Headers
        ttk.Label(grades_frame, text="Student", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(grades_frame, text="Score", font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(grades_frame, text="Grade", font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5)

        # Student entries (will be populated when assessment is selected)
        self.grade_entries = []
        self.grade_vars = []

        def load_students_for_assessment():
            # Clear existing entries
            for widget in grades_frame.winfo_children():
                if widget.grid_info()['row'] > 0:  # Skip headers
                    widget.destroy()

            if not assessment_var.get():
                return

            # Get assessment ID
            assessment_index = assessment_combo.current()
            if assessment_index < 0:
                return

            assessment_id = assessments[assessment_index]['id']

            # Get students
            conn = get_db_connection()
            students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()

            # Clear previous entries
            self.grade_entries.clear()
            self.grade_vars.clear()

            for i, student in enumerate(students, 1):
                # Student name
                ttk.Label(grades_frame, text=f"{student['student_id']} - {student['name']}").grid(row=i, column=0, padx=5, pady=2, sticky='w')

                # Score entry
                score_var = tk.StringVar()
                score_entry = ttk.Entry(grades_frame, textvariable=score_var, width=10)
                score_entry.grid(row=i, column=1, padx=5, pady=2)

                # Grade display (calculated)
                grade_label = ttk.Label(grades_frame, text="N/A", width=5)
                grade_label.grid(row=i, column=2, padx=5, pady=2)

                self.grade_entries.append((student['student_id'], score_var, grade_label))

                # Bind score change to update grade
                score_var.trace('w', lambda *args, sv=score_var, gl=grade_label, max_score=100: self.update_grade_display(sv, gl, max_score))

            conn.close()

        assessment_combo.bind('<<ComboboxSelected>>', lambda e: load_students_for_assessment())

        def save_grades():
            if not assessment_var.get():
                messagebox.showerror("Error", "Please select an assessment")
                return

            assessment_index = assessment_combo.current()
            assessment_id = assessments[assessment_index]['id']

            conn = get_db_connection()
            saved_count = 0

            for student_id, score_var, grade_label in self.grade_entries:
                score_text = score_var.get().strip()
                if score_text:
                    try:
                        score = float(score_text)
                        grade_letter = self.calculate_grade_letter(score)

                        # Insert or update grade
                        conn.execute("""
                            INSERT OR REPLACE INTO gradebook_grades
                            (student_id, assessment_id, score, grade_letter, recorded_by)
                            VALUES (?, ?, ?, ?, ?)
                        """, (student_id, assessment_id, score, grade_letter, self.current_user))

                        saved_count += 1

                    except ValueError:
                        continue

            conn.commit()
            conn.close()

            # Generate notifications for grade updates
            if saved_count > 0:
                assessment_name = assessment_var.get()
                subject_name = subject_var.get()
                for student_id, score_var, grade_label in self.grade_entries:
                    score_text = score_var.get().strip()
                    if score_text:
                        try:
                            score = float(score_text)
                            grade_letter = self.calculate_grade_letter(score)
                            generate_grade_notifications(student_id, assessment_name, grade_letter, subject_name)
                        except ValueError:
                            continue

            log_action(self.current_user, "Entered Grades", f"Saved {saved_count} grades for assessment {assessment_var.get()}")
            messagebox.showinfo("Success", f"Saved {saved_count} grades successfully!")
            dialog.destroy()
            self.load_grades()

        ttk.Button(dialog, text="Save Grades", command=save_grades).pack(pady=20)

    def update_grade_display(self, score_var, grade_label, max_score):
        """Update grade letter display when score changes"""
        try:
            score = float(score_var.get())
            grade = self.calculate_grade_letter(score)
            grade_label.config(text=grade)
        except (ValueError, AttributeError):
            grade_label.config(text="N/A")

    def calculate_grade_letter(self, score, max_score=100):
        """Calculate grade letter from score"""
        percentage = (score / max_score) * 100

        if percentage >= 90:
            return "A+"
        elif percentage >= 85:
            return "A"
        elif percentage >= 80:
            return "A-"
        elif percentage >= 75:
            return "B+"
        elif percentage >= 70:
            return "B"
        elif percentage >= 65:
            return "B-"
        elif percentage >= 60:
            return "C+"
        elif percentage >= 55:
            return "C"
        elif percentage >= 50:
            return "C-"
        elif percentage >= 45:
            return "D"
        else:
            return "F"

    def calculate_student_gpa(self):
        """Calculate GPA for selected student or all students"""
        # For now, show GPA calculation dialog
        dialog = tk.Toplevel(self)
        dialog.title("GPA Calculator")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Student:").pack(pady=10)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(dialog, textvariable=student_var, width=40)
        student_combo.pack(pady=5)

        # Load students
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
        student_list = [f"{s['student_id']} - {s['name']}" for s in students]
        student_combo['values'] = student_list
        conn.close()

        result_text = tk.Text(dialog, height=15, width=50)
        result_text.pack(pady=10)

        def calculate_gpa():
            if not student_var.get():
                messagebox.showerror("Error", "Please select a student")
                return

            student_id = student_var.get().split(" - ")[0]

            conn = get_db_connection()
            grades = conn.execute("""
                SELECT gg.score, ga.max_score, ga.weight, gc.weight as category_weight
                FROM gradebook_grades gg
                JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
                JOIN gradebook_categories gc ON ga.category_id = gc.id
                WHERE gg.student_id = ?
            """, (student_id,)).fetchall()
            conn.close()

            if not grades:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "No grades found for this student.")
                return

            total_weighted_score = 0
            total_weight = 0

            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"GPA Calculation for {student_var.get()}\n")
            result_text.insert(tk.END, "=" * 50 + "\n\n")

            for grade in grades:
                if grade['score'] and grade['max_score']:
                    percentage = (grade['score'] / grade['max_score']) * 100
                    weighted_score = percentage * grade['weight'] * grade['category_weight']
                    total_weighted_score += weighted_score
                    total_weight += (grade['weight'] * grade['category_weight'])

                    result_text.insert(tk.END, f"Score: {grade['score']:.1f}/{grade['max_score']:.1f} "
                                             f"({percentage:.1f}%) Weight: {grade['weight'] * grade['category_weight']:.2f}\n")

            if total_weight > 0:
                gpa_percentage = total_weighted_score / total_weight
                gpa = self.percentage_to_gpa(gpa_percentage)

                result_text.insert(tk.END, f"\nTotal Weighted Score: {total_weighted_score:.2f}\n")
                result_text.insert(tk.END, f"Total Weight: {total_weight:.2f}\n")
                result_text.insert(tk.END, f"Overall Percentage: {gpa_percentage:.2f}%\n")
                result_text.insert(tk.END, f"GPA: {gpa:.2f}\n")
            else:
                result_text.insert(tk.END, "Unable to calculate GPA - no valid grades found.\n")

        ttk.Button(dialog, text="Calculate GPA", command=calculate_gpa).pack(pady=10)

    def percentage_to_gpa(self, percentage):
        """Convert percentage to GPA (4.0 scale)"""
        if percentage >= 90:
            return 4.0
        elif percentage >= 85:
            return 3.7
        elif percentage >= 80:
            return 3.3
        elif percentage >= 75:
            return 3.0
        elif percentage >= 70:
            return 2.7
        elif percentage >= 65:
            return 2.3
        elif percentage >= 60:
            return 2.0
        elif percentage >= 55:
            return 1.7
        elif percentage >= 50:
            return 1.3
        elif percentage >= 45:
            return 1.0
        else:
            return 0.0

    def show_grade_analytics(self):
        """Show grade analytics and statistics"""
        dialog = tk.Toplevel(self)
        dialog.title("Grade Analytics")
        dialog.geometry("700x500")
        dialog.transient(self)
        dialog.grab_set()

        # Analytics content
        analytics_text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        analytics_text.pack(fill=tk.BOTH, expand=True)

        conn = get_db_connection()

        # Overall statistics
        stats = conn.execute("""
            SELECT
                COUNT(*) as total_grades,
                AVG(gg.score/ga.max_score * 100) as avg_percentage,
                MIN(gg.score/ga.max_score * 100) as min_percentage,
                MAX(gg.score/ga.max_score * 100) as max_percentage
            FROM gradebook_grades gg
            JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
            WHERE gg.score IS NOT NULL
        """).fetchone()

        analytics_text.insert(tk.END, "📊 GRADE ANALYTICS REPORT\n")
        analytics_text.insert(tk.END, "=" * 50 + "\n\n")

        if stats['total_grades']:
            analytics_text.insert(tk.END, f"Total Grades Recorded: {stats['total_grades']}\n")
            analytics_text.insert(tk.END, f"Average Percentage: {stats['avg_percentage']:.2f}%\n")
            analytics_text.insert(tk.END, f"Highest Score: {stats['max_percentage']:.2f}%\n")
            analytics_text.insert(tk.END, f"Lowest Score: {stats['min_percentage']:.2f}%\n\n")

        # Grade distribution
        analytics_text.insert(tk.END, "🎯 GRADE DISTRIBUTION\n")
        analytics_text.insert(tk.END, "-" * 30 + "\n")

        grade_dist = conn.execute("""
            SELECT gg.grade_letter, COUNT(*) as count
            FROM gradebook_grades gg
            WHERE gg.grade_letter IS NOT NULL
            GROUP BY gg.grade_letter
            ORDER BY count DESC
        """).fetchall()

        for grade in grade_dist:
            analytics_text.insert(tk.END, f"Grade {grade['grade_letter']}: {grade['count']} students\n")

        # Top performers
        analytics_text.insert(tk.END, "\n🏆 TOP PERFORMERS\n")
        analytics_text.insert(tk.END, "-" * 20 + "\n")

        top_students = conn.execute("""
            SELECT s.name, AVG(gg.score/ga.max_score * 100) as avg_score, COUNT(*) as assessments
            FROM gradebook_grades gg
            JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
            JOIN students s ON gg.student_id = s.student_id
            WHERE gg.score IS NOT NULL
            GROUP BY gg.student_id, s.name
            HAVING assessments >= 3
            ORDER BY avg_score DESC
            LIMIT 5
        """).fetchall()

        for i, student in enumerate(top_students, 1):
            analytics_text.insert(tk.END, f"{i}. {student['name']}: {student['avg_score']:.2f}% "
                                         f"({student['assessments']} assessments)\n")

        conn.close()

        analytics_text.config(state=tk.DISABLED)

    def generate_report_card_dialog(self):
        """Dialog to generate report cards"""
        dialog = tk.Toplevel(self)
        dialog.title("Generate Report Card")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Student:").pack(pady=10)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(dialog, textvariable=student_var, width=40)
        student_combo.pack(pady=5)

        # Load students
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, name FROM students ORDER BY name").fetchall()
        student_list = [f"{s['student_id']} - {s['name']}" for s in students]
        student_combo['values'] = student_list

        ttk.Label(dialog, text="Academic Year:").pack(pady=10)
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(dialog, textvariable=year_var, width=40)
        year_combo.pack(pady=5)

        # Load academic years
        years = conn.execute("SELECT year_name FROM academic_years ORDER BY start_date DESC").fetchall()
        year_list = [y['year_name'] for y in years]
        year_combo['values'] = year_list
        conn.close()

        ttk.Label(dialog, text="Semester:").pack(pady=10)
        semester_var = tk.StringVar(value="Annual")
        semester_combo = ttk.Combobox(dialog, textvariable=semester_var,
                                    values=["Semester 1", "Semester 2", "Annual"])
        semester_combo.pack(pady=5)

        def generate_report():
            if not student_var.get() or not year_var.get():
                messagebox.showerror("Error", "Please fill in all fields")
                return

            student_id = student_var.get().split(" - ")[0]

            conn = get_db_connection()
            year_id = conn.execute("SELECT id FROM academic_years WHERE year_name = ?", (year_var.get(),)).fetchone()['id']

            # Calculate GPA
            grades = conn.execute("""
                SELECT gg.score, ga.max_score, ga.weight, gc.weight as category_weight, gc.subject_name
                FROM gradebook_grades gg
                JOIN gradebook_assessments ga ON gg.assessment_id = ga.id
                JOIN gradebook_categories gc ON ga.category_id = gc.id
                WHERE gg.student_id = ?
            """, (student_id,)).fetchall()

            if not grades:
                messagebox.showerror("Error", "No grades found for this student")
                conn.close()
                return

            # Calculate GPA
            total_weighted_score = 0
            total_weight = 0
            subject_grades = {}

            for grade in grades:
                if grade['score'] and grade['max_score']:
                    percentage = (grade['score'] / grade['max_score']) * 100
                    weight = grade['weight'] * grade['category_weight']
                    total_weighted_score += (percentage * weight)
                    total_weight += weight

                    subject = grade['subject_name'] or 'General'
                    if subject not in subject_grades:
                        subject_grades[subject] = []
                    subject_grades[subject].append(percentage)

            gpa = 0
            if total_weight > 0:
                overall_percentage = total_weighted_score / total_weight
                gpa = self.percentage_to_gpa(overall_percentage)

            # Insert report card
            cursor = conn.execute("""
                INSERT INTO report_cards (student_id, academic_year_id, semester, gpa, status, generated_by)
                VALUES (?, ?, ?, ?, 'Generated', ?)
            """, (student_id, year_id, semester_var.get(), gpa, self.current_user))

            report_card_id = cursor.lastrowid

            # Insert subject details
            for subject, percentages in subject_grades.items():
                avg_percentage = sum(percentages) / len(percentages)
                final_grade = self.calculate_grade_letter(avg_percentage)
                credits = 3.0  # Default credits

                conn.execute("""
                    INSERT INTO report_card_details (report_card_id, subject_name, final_grade, score, credits)
                    VALUES (?, ?, ?, ?, ?)
                """, (report_card_id, subject, final_grade, avg_percentage, credits))

            conn.commit()
            conn.close()

            # Generate report card notification
            generate_report_card_notifications(student_id, year_var.get(), semester_var.get(), gpa)

            log_action(self.current_user, "Generated Report Card", f"Student: {student_id}, GPA: {gpa:.2f}")
            messagebox.showinfo("Success", f"Report card generated successfully!\nGPA: {gpa:.2f}")
            dialog.destroy()
            self.load_report_cards()

        ttk.Button(dialog, text="Generate Report Card", command=generate_report).pack(pady=20)

    def view_report_card(self):
        """View selected report card"""
        selected = self.report_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report card to view")
            return

        item = self.report_tree.item(selected[0])
        values = item['values']
        student_id = values[0]

        # Find report card ID
        conn = get_db_connection()
        report_card = conn.execute("""
            SELECT rc.*, ay.year_name, s.name as student_name
            FROM report_cards rc
            JOIN academic_years ay ON rc.academic_year_id = ay.id
            JOIN students s ON rc.student_id = s.student_id
            WHERE rc.student_id = ? AND ay.year_name = ?
        """, (student_id, values[2])).fetchone()

        if not report_card:
            messagebox.showerror("Error", "Report card not found")
            conn.close()
            return

        # Get subject details
        details = conn.execute("""
            SELECT * FROM report_card_details
            WHERE report_card_id = ?
            ORDER BY subject_name
        """, (report_card['id'],)).fetchall()
        conn.close()

        # Display report card
        dialog = tk.Toplevel(self)
        dialog.title(f"Report Card - {report_card['student_name']}")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()

        # Header
        header_frame = ttk.Frame(dialog)
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(header_frame, text=f"Student: {report_card['student_name']} ({student_id})",
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        ttk.Label(header_frame, text=f"Academic Year: {report_card['year_name']}").pack(anchor='w')
        ttk.Label(header_frame, text=f"Semester: {report_card['semester']}").pack(anchor='w')
        ttk.Label(header_frame, text=f"GPA: {report_card['gpa']:.2f}",
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 0))

        # Subjects table
        table_frame = ttk.Frame(dialog)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Headers
        ttk.Label(table_frame, text="Subject", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(table_frame, text="Grade", font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(table_frame, text="Score (%)", font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(table_frame, text="Credits", font=('Segoe UI', 9, 'bold')).grid(row=0, column=3, padx=5, pady=5)

        # Subject data
        for i, detail in enumerate(details, 1):
            ttk.Label(table_frame, text=detail['subject_name']).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            ttk.Label(table_frame, text=detail['final_grade']).grid(row=i, column=1, padx=5, pady=2)
            ttk.Label(table_frame, text=f"{detail['score']:.1f}%").grid(row=i, column=2, padx=5, pady=2)
            ttk.Label(table_frame, text=f"{detail['credits']:.1f}").grid(row=i, column=3, padx=5, pady=2)

    def print_report_card(self):
        """Print report card (placeholder for actual printing functionality)"""
        messagebox.showinfo("Print Report Card", "Print functionality will be implemented in the next version.\n\nFor now, you can view the report card and manually print the window.")

    def show_academic_summary(self):
        """Show academic summary for all students"""
        dialog = tk.Toplevel(self)
        dialog.title("Academic Summary")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()

        summary_text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        summary_text.pack(fill=tk.BOTH, expand=True)

        conn = get_db_connection()

        # Class statistics
        stats = conn.execute("""
            SELECT
                COUNT(DISTINCT rc.student_id) as students_with_reports,
                AVG(rc.gpa) as avg_gpa,
                MAX(rc.gpa) as max_gpa,
                MIN(rc.gpa) as min_gpa
            FROM report_cards rc
        """).fetchone()

        summary_text.insert(tk.END, "📊 ACADEMIC SUMMARY REPORT\n")
        summary_text.insert(tk.END, "=" * 50 + "\n\n")

        if stats['students_with_reports']:
            summary_text.insert(tk.END, f"Students with Report Cards: {stats['students_with_reports']}\n")
            summary_text.insert(tk.END, f"Class Average GPA: {stats['avg_gpa']:.2f}\n")
            summary_text.insert(tk.END, f"Highest GPA: {stats['max_gpa']:.2f}\n")
            summary_text.insert(tk.END, f"Lowest GPA: {stats['min_gpa']:.2f}\n\n")

        # GPA distribution
        summary_text.insert(tk.END, "🎯 GPA DISTRIBUTION\n")
        summary_text.insert(tk.END, "-" * 20 + "\n")

        gpa_ranges = conn.execute("""
            SELECT
                CASE
                    WHEN gpa >= 3.7 THEN 'A (3.7-4.0)'
                    WHEN gpa >= 3.0 THEN 'B (3.0-3.6)'
                    WHEN gpa >= 2.0 THEN 'C (2.0-2.9)'
                    WHEN gpa >= 1.0 THEN 'D (1.0-1.9)'
                    ELSE 'F (0.0-0.9)'
                END as range,
                COUNT(*) as count
            FROM report_cards
            GROUP BY
                CASE
                    WHEN gpa >= 3.7 THEN 'A (3.7-4.0)'
                    WHEN gpa >= 3.0 THEN 'B (3.0-3.6)'
                    WHEN gpa >= 2.0 THEN 'C (2.0-2.9)'
                    WHEN gpa >= 1.0 THEN 'D (1.0-1.9)'
                    ELSE 'F (0.0-0.9)'
                END
            ORDER BY range
        """).fetchall()

        for gpa_range in gpa_ranges:
            summary_text.insert(tk.END, f"{gpa_range['range']}: {gpa_range['count']} students\n")

        # Top 10 students
        summary_text.insert(tk.END, "\n🏆 TOP 10 STUDENTS BY GPA\n")
        summary_text.insert(tk.END, "-" * 25 + "\n")

        top_students = conn.execute("""
            SELECT s.name, rc.gpa, rc.semester
            FROM report_cards rc
            JOIN students s ON rc.student_id = s.student_id
            ORDER BY rc.gpa DESC
            LIMIT 10
        """).fetchall()

        for i, student in enumerate(top_students, 1):
            summary_text.insert(tk.END, f"{i}. {student['name']}: {student['gpa']:.2f} ({student['semester']})\n")

        conn.close()

        summary_text.config(state=tk.DISABLED)

    def add_assessment_dialog(self):
        """Dialog to add new assessment"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Assessment")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Category:").pack(pady=10)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, width=40)
        category_combo.pack(pady=5)

        # Load categories
        conn = get_db_connection()
        categories = conn.execute("SELECT id, name FROM gradebook_categories WHERE is_active = 1 ORDER BY name").fetchall()
        category_list = [c['name'] for c in categories]
        category_combo['values'] = category_list
        conn.close()

        ttk.Label(dialog, text="Assessment Name:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)

        ttk.Label(dialog, text="Maximum Score:").pack(pady=10)
        max_score_var = tk.StringVar(value="100")
        ttk.Entry(dialog, textvariable=max_score_var).pack(pady=5)

        ttk.Label(dialog, text="Weight (0.0-1.0):").pack(pady=10)
        weight_var = tk.StringVar(value="1.0")
        ttk.Entry(dialog, textvariable=weight_var).pack(pady=5)

        ttk.Label(dialog, text="Assessment Date (YYYY-MM-DD):").pack(pady=10)
        date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        ttk.Entry(dialog, textvariable=date_var).pack(pady=5)

        def save_assessment():
            if not category_var.get() or not name_var.get():
                messagebox.showerror("Error", "Please fill in category and assessment name")
                return

            try:
                max_score = float(max_score_var.get())
                weight = float(weight_var.get())

                if not 0 <= weight <= 1:
                    messagebox.showerror("Error", "Weight must be between 0.0 and 1.0")
                    return

                conn = get_db_connection()
                category_id = None
                for cat in categories:
                    if cat['name'] == category_var.get():
                        category_id = cat['id']
                        break

                if category_id:
                    conn.execute("""
                        INSERT INTO gradebook_assessments (category_id, assessment_name, max_score, weight, assessment_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (category_id, name_var.get(), max_score, weight, date_var.get()))

                    conn.commit()
                    log_action(self.current_user, "Added Assessment", f"Assessment: {name_var.get()}")
                    messagebox.showinfo("Success", "Assessment added successfully!")
                    dialog.destroy()
                    self.load_assessments()

                conn.close()

            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values")

        ttk.Button(dialog, text="Save Assessment", command=save_assessment).pack(pady=20)

    def add_category_dialog(self):
        """Dialog to add new gradebook category"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Category")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Category Name:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var).pack(pady=5)

        ttk.Label(dialog, text="Weight (0.0-1.0):").pack(pady=10)
        weight_var = tk.StringVar(value="1.0")
        ttk.Entry(dialog, textvariable=weight_var).pack(pady=5)

        ttk.Label(dialog, text="Subject (optional):").pack(pady=10)
        subject_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=subject_var).pack(pady=5)

        def save_category():
            if not name_var.get():
                messagebox.showerror("Error", "Category name is required")
                return

            try:
                weight = float(weight_var.get())
                if not 0 <= weight <= 1:
                    messagebox.showerror("Error", "Weight must be between 0.0 and 1.0")
                    return

                conn = get_db_connection()
                conn.execute("""
                    INSERT INTO gradebook_categories (name, description, weight, subject_name)
                    VALUES (?, ?, ?, ?)
                """, (name_var.get(), desc_var.get(), weight, subject_var.get() or None))

                conn.commit()
                log_action(self.current_user, "Added Category", f"Category: {name_var.get()}")
                messagebox.showinfo("Success", "Category added successfully!")
                dialog.destroy()
                self.load_assessments()
                self.load_subjects_filter()

                conn.close()

            except ValueError:
                messagebox.showerror("Error", "Invalid weight value")

        ttk.Button(dialog, text="Save Category", command=save_category).pack(pady=20)

    def manage_academic_year_dialog(self):
        """Dialog to manage academic years"""
        dialog = tk.Toplevel(self)
        dialog.title("Academic Year Management")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Current academic years list
        ttk.Label(dialog, text="Current Academic Years:").pack(pady=10)

        years_frame = ttk.Frame(dialog)
        years_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Headers
        ttk.Label(years_frame, text="Year", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(years_frame, text="Start Date", font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(years_frame, text="End Date", font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(years_frame, text="Current", font=('Segoe UI', 9, 'bold')).grid(row=0, column=3, padx=5, pady=5)

        conn = get_db_connection()
        years = conn.execute("SELECT * FROM academic_years ORDER BY start_date DESC").fetchall()
        conn.close()

        for i, year in enumerate(years, 1):
            ttk.Label(years_frame, text=year['year_name']).grid(row=i, column=0, padx=5, pady=2)
            ttk.Label(years_frame, text=year['start_date']).grid(row=i, column=1, padx=5, pady=2)
            ttk.Label(years_frame, text=year['end_date']).grid(row=i, column=2, padx=5, pady=2)
            ttk.Label(years_frame, text="✓" if year['is_current'] else "").grid(row=i, column=3, padx=5, pady=2)

        # Add new year section
        ttk.Label(dialog, text="Add New Academic Year:").pack(pady=10)

        new_year_frame = ttk.Frame(dialog)
        new_year_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(new_year_frame, text="Year Name:").grid(row=0, column=0, padx=5, pady=5)
        year_name_var = tk.StringVar()
        ttk.Entry(new_year_frame, textvariable=year_name_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(new_year_frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5)
        start_date_var = tk.StringVar()
        ttk.Entry(new_year_frame, textvariable=start_date_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(new_year_frame, text="End Date:").grid(row=2, column=0, padx=5, pady=5)
        end_date_var = tk.StringVar()
        ttk.Entry(new_year_frame, textvariable=end_date_var).grid(row=2, column=1, padx=5, pady=5)

        def add_year():
            if not year_name_var.get() or not start_date_var.get() or not end_date_var.get():
                messagebox.showerror("Error", "Please fill in all fields")
                return

            conn = get_db_connection()
            try:
                # Set all years to not current first
                conn.execute("UPDATE academic_years SET is_current = 0")

                # Add new year
                conn.execute("""
                    INSERT INTO academic_years (year_name, start_date, end_date, is_current)
                    VALUES (?, ?, ?, 1)
                """, (year_name_var.get(), start_date_var.get(), end_date_var.get()))

                conn.commit()
                log_action(self.current_user, "Added Academic Year", f"Year: {year_name_var.get()}")
                messagebox.showinfo("Success", "Academic year added successfully!")
                dialog.destroy()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Academic year name already exists")
            finally:
                conn.close()

        ttk.Button(dialog, text="Add Academic Year", command=add_year).pack(pady=10)

    # ----------------------
    # SUBJECTS & MARKS
    # ----------------------
    def show_subjects(self):
        self.clear_main_area()
        
        # Toolbar
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="➕ Add Marks", command=self.add_marks_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="🗑️ Delete Selected", command=self.delete_marks).pack(side=tk.LEFT, padx=5)
        
        # Tree
        cols = ["ID", "Student ID", "Name", "Subject", "Marks", "Grade", "Semester"]
        self.sub_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            self.sub_tree.heading(c, text=c)
            self.sub_tree.column(c, width=150)
        self.sub_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.load_marks()

    def load_marks(self):
        self.sub_tree.delete(*self.sub_tree.get_children())
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT s.id, s.student_id, st.name, s.subject_name, s.marks, s.semester
            FROM subjects s
            JOIN students st ON s.student_id = st.student_id
            ORDER BY s.id DESC
        ''')
        for r in c.fetchall():
            grade = self.calculate_grade(r['marks'])
            self.sub_tree.insert("", tk.END, values=(r['id'], r['student_id'], r['name'], r['subject_name'], r['marks'], grade, r['semester']))
        conn.close()

    def calculate_grade(self, marks):
        if marks >= 90:
            return 'A+'
        elif marks >= 80:
            return 'A'
        elif marks >= 70:
            return 'B'
        elif marks >= 60:
            return 'C'
        elif marks >= 50:
            return 'D'
        else:
            return 'F'

    def add_marks_dialog(self):
        win = tk.Toplevel(self)
        win.geometry("400x300")
        win.title("Add Subject Marks")
        win.transient(self)
        win.grab_set()
        
        f = ttk.Frame(win, padding=20)
        f.pack(expand=True, fill=tk.BOTH)
        
        # Student Selector
        ttk.Label(f, text="Student ID:").grid(row=0, column=0, sticky='w')
        sid_entry = ttk.Entry(f)
        sid_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Subject:").grid(row=1, column=0, sticky='w')
        sub_entry = ttk.Entry(f)
        sub_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Marks (0-100):").grid(row=2, column=0, sticky='w')
        marks_entry = ttk.Entry(f)
        marks_entry.grid(row=2, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Semester:").grid(row=3, column=0, sticky='w')
        sem_entry = ttk.Entry(f)
        sem_entry.grid(row=3, column=1, sticky='ew', pady=5)

        def save():
            try:
                student_id = sid_entry.get().strip()
                subject = sub_entry.get().strip()
                marks = float(marks_entry.get().strip())
                semester = sem_entry.get().strip()
                
                if not student_id or not subject:
                    messagebox.showerror("Error", "Student ID and Subject are required")
                    return
                if not (0 <= marks <= 100):
                    messagebox.showerror("Error", "Marks must be between 0 and 100")
                    return
                
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO subjects (student_id, subject_name, marks, semester) VALUES (?, ?, ?, ?)",
                          (student_id, subject, marks, semester))
                conn.commit()
                conn.close()
                log_action(self.current_user, "ADD_MARKS", f"Added {subject} for {student_id}")
                messagebox.showinfo("Success", "Marks added successfully")
                win.destroy()
                self.load_marks()
            except ValueError:
                messagebox.showerror("Error", "Invalid marks value")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(f, text="Save", command=save).grid(row=4, column=1, pady=10)

    def delete_marks(self):
        selected = self.sub_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected marks?"):
            for item in selected:
                mark_id = self.sub_tree.item(item)['values'][0]
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("DELETE FROM subjects WHERE id=?", (mark_id,))
                conn.commit()
                conn.close()
            log_action(self.current_user, "DELETE_MARKS", f"Deleted {len(selected)} marks")
            self.load_marks()

    # ----------------------
    # TUTORIALS
    # ----------------------
    def show_tutorials(self):
        self.clear_main_area()
        
        # Toolbar
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="➕ Add Tutorial", command=self.add_tutorial_dialog).pack(side=tk.LEFT) if self.user_role == 'admin' else None
        ttk.Button(tb, text="🗑️ Delete Selected", command=self.delete_tutorial).pack(side=tk.LEFT, padx=5) if self.user_role == 'admin' else None
        
        # Tree
        cols = ["ID", "Title", "Subject", "Description", "Uploaded By", "Date"]
        self.tut_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            self.tut_tree.heading(c, text=c)
            self.tut_tree.column(c, width=120)
        self.tut_tree.column("Description", width=200)
        self.tut_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Watch button
        ttk.Button(tb, text="▶️ Watch Selected", command=self.watch_tutorial).pack(side=tk.RIGHT)
        
        self.load_tutorials()

    def load_tutorials(self):
        self.tut_tree.delete(*self.tut_tree.get_children())
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tutorials ORDER BY id DESC")
        for r in c.fetchall():
            self.tut_tree.insert("", tk.END, values=(r['id'], r['title'], r['subject'] or '', r['description'] or '', r['uploaded_by'] or '', r['created_at'][:10]))
        conn.close()

    def add_tutorial_dialog(self):
        win = tk.Toplevel(self)
        win.geometry("500x400")
        win.title("Add Tutorial")
        win.transient(self)
        win.grab_set()
        
        f = ttk.Frame(win, padding=20)
        f.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(f, text="Title:").grid(row=0, column=0, sticky='w', pady=5)
        title_entry = ttk.Entry(f)
        title_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Subject:").grid(row=1, column=0, sticky='w', pady=5)
        subject_entry = ttk.Entry(f)
        subject_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Description:").grid(row=2, column=0, sticky='w', pady=5)
        desc_entry = tk.Text(f, height=3)
        desc_entry.grid(row=2, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Video URL:").grid(row=3, column=0, sticky='w', pady=5)
        url_entry = ttk.Entry(f)
        url_entry.grid(row=3, column=1, sticky='ew', pady=5)
        
        def save():
            title = title_entry.get()
            subject = subject_entry.get()
            desc = desc_entry.get("1.0", tk.END).strip()
            url = url_entry.get()
            
            if not title or not url:
                messagebox.showerror("Error", "Title and Video URL are required")
                return
            
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO tutorials (title, subject, description, video_url, uploaded_by) VALUES (?, ?, ?, ?, ?)",
                      (title, subject, desc, url, self.current_user))
            conn.commit()
            conn.close()
            log_action(self.current_user, "ADD_TUTORIAL", f"Added tutorial: {title}")
            messagebox.showinfo("Success", "Tutorial added successfully")
            win.destroy()
            self.load_tutorials()
        
        ttk.Button(f, text="Save", command=save).grid(row=4, column=1, pady=20)

    def delete_tutorial(self):
        selected = self.tut_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected tutorial(s)?"):
            for item in selected:
                tut_id = self.tut_tree.item(item)['values'][0]
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("DELETE FROM tutorials WHERE id=?", (tut_id,))
                conn.commit()
                conn.close()
            log_action(self.current_user, "DELETE_TUTORIAL", f"Deleted {len(selected)} tutorials")
            self.load_tutorials()

    def watch_tutorial(self):
        selected = self.tut_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a tutorial first.")
            return
        
        tut_id = self.tut_tree.item(selected[0])['values'][0]
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT video_url FROM tutorials WHERE id=?", (tut_id,))
        row = c.fetchone()
        conn.close()
        
        if row and row['video_url']:
            import webbrowser
            webbrowser.open(row['video_url'])
        else:
            messagebox.showinfo("No URL", "No video URL available for this tutorial.")

    # ----------------------
    # STUDY NOTES
    # ----------------------
    def show_study_notes(self):
        self.clear_main_area()
        
        # Toolbar
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="➕ Upload Notes", command=self.upload_notes_dialog).pack(side=tk.LEFT) if self.user_role == 'admin' else None
        ttk.Button(tb, text="🗑️ Delete Selected", command=self.delete_notes).pack(side=tk.LEFT, padx=5) if self.user_role == 'admin' else None
        
        # Tree
        cols = ["ID", "Title", "Subject", "Uploaded By", "Date"]
        self.notes_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            self.notes_tree.heading(c, text=c)
            self.notes_tree.column(c, width=120)
        self.notes_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Download button
        ttk.Button(tb, text="⬇️ Download Selected", command=self.download_notes).pack(side=tk.RIGHT)
        
        self.load_study_notes()

    def load_study_notes(self):
        self.notes_tree.delete(*self.notes_tree.get_children())
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM study_notes ORDER BY id DESC")
        for r in c.fetchall():
            self.notes_tree.insert("", tk.END, values=(r['id'], r['title'], r['subject'] or '', r['uploaded_by'] or '', r['created_at'][:10]))
        conn.close()

    def upload_notes_dialog(self):
        win = tk.Toplevel(self)
        win.geometry("500x300")
        win.title("Upload Study Notes")
        win.transient(self)
        win.grab_set()
        
        f = ttk.Frame(win, padding=20)
        f.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(f, text="Title:").grid(row=0, column=0, sticky='w', pady=5)
        title_entry = ttk.Entry(f)
        title_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Subject:").grid(row=1, column=0, sticky='w', pady=5)
        subject_entry = ttk.Entry(f)
        subject_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="File:").grid(row=2, column=0, sticky='w', pady=5)
        file_var = tk.StringVar()
        ttk.Entry(f, textvariable=file_var, state='readonly').grid(row=2, column=1, sticky='ew', pady=5)
        ttk.Button(f, text="Browse", command=lambda: self.select_file(file_var)).grid(row=2, column=2, padx=5)
        
        def save():
            title = title_entry.get()
            subject = subject_entry.get()
            file_path = file_var.get()
            
            if not title or not file_path:
                messagebox.showerror("Error", "Title and file are required")
                return
            
            # Copy file to notes folder
            safe_title = ''.join(c if c.isalnum() or c in (' ', '_') else '_' for c in title).strip().replace(' ', '_')
            dest_path = self.safe_copy_file(file_path, "notes", safe_title)
            
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO study_notes (title, subject, file_path, uploaded_by) VALUES (?, ?, ?, ?)",
                      (title, subject, dest_path, self.current_user))
            conn.commit()
            conn.close()
            log_action(self.current_user, "UPLOAD_NOTES", f"Uploaded notes: {title}")
            messagebox.showinfo("Success", "Notes uploaded successfully")
            win.destroy()
            self.load_study_notes()
        
        ttk.Button(f, text="Upload", command=save).grid(row=3, column=1, pady=20)

    def select_file(self, var):
        file_path = filedialog.askopenfilename(
            title="Select Notes File",
            filetypes=[("Document files", "*.pdf *.doc *.docx *.txt"), ("All files", "*.*")]
        )
        if file_path:
            var.set(file_path)

    def delete_notes(self):
        selected = self.notes_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected notes?"):
            for item in selected:
                note_id = self.notes_tree.item(item)['values'][0]
                # Get file path to delete file too
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT file_path FROM study_notes WHERE id=?", (note_id,))
                row = c.fetchone()
                if row and row['file_path'] and os.path.exists(row['file_path']):
                    os.remove(row['file_path'])
                c.execute("DELETE FROM study_notes WHERE id=?", (note_id,))
                conn.commit()
                conn.close()
            log_action(self.current_user, "DELETE_NOTES", f"Deleted {len(selected)} notes")
            self.load_study_notes()

    def download_notes(self):
        selected = self.notes_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select notes to download.")
            return
        
        note_id = self.notes_tree.item(selected[0])['values'][0]
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT file_path FROM study_notes WHERE id=?", (note_id,))
        row = c.fetchone()
        conn.close()
        
        if row and row['file_path'] and os.path.exists(row['file_path']):
            os.startfile(row['file_path'])
        else:
            messagebox.showinfo("File Not Found", "The notes file is not available.")

    # ----------------------
    def show_analytics(self):
        self.clear_main_area()
        
        # Tabs
        nb = ttk.Notebook(self.main_area)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tab1 = ttk.Frame(nb)
        tab2 = ttk.Frame(nb)
        tab3 = ttk.Frame(nb)
        
        nb.add(tab1, text="Charts")
        nb.add(tab2, text="Top Performers")
        nb.add(tab3, text="Attendance Summary")
        
        # Draw Charts if matplotlib available
        if HAS_MATPLOTLIB:
            self.draw_charts(tab1)
        else:
            ttk.Label(tab1, text="matplotlib not installed. Install with 'pip install matplotlib' for charts.").pack(pady=20)
        
        # Top Performers List
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT st.name, AVG(s.marks) as avg_mark
            FROM subjects s
            JOIN students st ON s.student_id = st.student_id
            GROUP BY s.student_id
            ORDER BY avg_mark DESC
            LIMIT 10
        ''')
        top = c.fetchall()
        conn.close()
        
        tr = ttk.Treeview(tab2, columns=["Rank", "Name", "Avg Score"], show="headings")
        tr.pack(fill=tk.BOTH, expand=True)
        for c in tr['columns']:
            tr.heading(c, text=c)
            tr.column(c, width=150)
        
        for i, r in enumerate(top, 1):
            tr.insert("", tk.END, values=(i, r['name'], f"{r['avg_mark']:.2f}"))
        
        # Attendance Summary
        att_frame = ttk.Frame(tab3)
        att_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Simple summary: count present/absent/late for last 30 days
        conn = get_db_connection()
        c = conn.cursor()
        thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        c.execute('''
            SELECT status, COUNT(*) as cnt
            FROM attendance
            WHERE date >= ?
            GROUP BY status
        ''', (thirty_days_ago,))
        att_summary = c.fetchall()
        conn.close()
        
        if att_summary:
            for row in att_summary:
                ttk.Label(att_frame, text=f"{row['status']}: {row['cnt']}").pack(anchor='w')
        else:
            ttk.Label(att_frame, text="No attendance records in the last 30 days.").pack()

    def draw_charts(self, container):
        # 1. Pass/Fail Distribution
        fig, ax = plt.subplots(figsize=(5, 4))
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT marks FROM subjects")
        data = c.fetchall()
        conn.close()
        
        passed = len([x for x in data if x['marks'] >= 50])
        failed = len(data) - passed
        
        ax.pie([passed, failed], labels=['Passed', 'Failed'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
        ax.set_title("Pass/Fail Ratio")
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10)
        
        # 2. Program Distribution
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT program, COUNT(*) as cnt FROM students GROUP BY program")
        prog_data = c.fetchall()
        conn.close()
        
        if prog_data:
            ax2.bar([r['program'] for r in prog_data], [r['cnt'] for r in prog_data], color="#3498db")
            ax2.set_title("Students per Program")
            ax2.tick_params(axis='x', rotation=45)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=container)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)

    # ----------------------
    # ATTENDANCE
    # ----------------------
    def show_attendance(self):
        self.clear_main_area()
        
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(tb, text="Mark Attendance (Today)", command=self.mark_attendance_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="Refresh", command=self.load_attendance).pack(side=tk.LEFT, padx=5)
        
        cols = ["Student ID", "Name", "Date", "Status"]
        self.att_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            self.att_tree.heading(c, text=c)
            self.att_tree.column(c, width=150)
        self.att_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.load_attendance()

    def load_attendance(self):
        self.att_tree.delete(*self.att_tree.get_children())
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT a.student_id, s.name, a.date, a.status 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            ORDER BY a.date DESC
            LIMIT 100
        ''')
        for r in c.fetchall():
            self.att_tree.insert("", tk.END, values=(r['student_id'], r['name'], r['date'], r['status']))
        conn.close()

    def mark_attendance_dialog(self):
        win = tk.Toplevel(self)
        win.geometry("500x500")
        win.title("Mark Attendance")
        win.transient(self)
        win.grab_set()
        
        ttk.Label(win, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(win)
        date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack()
        
        # List of students with scrollbar
        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate students
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT student_id, name FROM students ORDER BY name")
        students = c.fetchall()
        conn.close()
        
        # Store attendance status for each student
        att_vars = {}
        for i, stu in enumerate(students):
            ttk.Label(scrollable_frame, text=f"{stu['name']} ({stu['student_id']})").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            status_combo = ttk.Combobox(scrollable_frame, values=["Present", "Absent", "Late"], width=10)
            status_combo.current(0)
            status_combo.grid(row=i, column=1, padx=5, pady=2)
            att_vars[stu['student_id']] = status_combo
        
        def save_attendance():
            date = date_entry.get().strip()
            if not date:
                messagebox.showerror("Error", "Date is required")
                return
            
            conn = get_db_connection()
            c = conn.cursor()
            count = 0
            for sid, combo in att_vars.items():
                status = combo.get()
                if status:
                    # Check if already marked for this date
                    c.execute("SELECT id FROM attendance WHERE student_id=? AND date=?", (sid, date))
                    existing = c.fetchone()
                    if existing:
                        c.execute("UPDATE attendance SET status=? WHERE student_id=? AND date=?", (status, sid, date))
                    else:
                        c.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (sid, date, status))
                    count += 1
            conn.commit()
            conn.close()
            log_action(self.current_user, "MARK_ATTENDANCE", f"Marked attendance for {count} students on {date}")
            messagebox.showinfo("Success", f"Attendance recorded for {count} students")
            win.destroy()
            self.load_attendance()
        
        ttk.Button(win, text="Save All", command=save_attendance).pack(pady=10)

    # ----------------------
    # SYSTEM TOOLS
    # ----------------------
    def show_settings(self):
        self.clear_main_area()
        
        f = ttk.Frame(self.main_area, padding=20)
        f.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(f, text="System Settings", font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=10)
        
        # Feature: Backup
        ttk.Button(f, text="💾 Backup Database to File", command=self.backup_db).pack(fill=tk.X, pady=5)
        ttk.Button(f, text="� Restore Database from Backup", command=self.restore_db).pack(fill=tk.X, pady=5)
        ttk.Button(f, text="�🗑️ Clear All Logs", command=self.clear_logs).pack(fill=tk.X, pady=5)
        
        # Theme Selector
        ttk.Label(f, text="Theme:").pack(anchor='w', pady=(20, 5))
        theme_combo = ttk.Combobox(f, values=["Light", "Dark"])
        theme_combo.pack(fill=tk.X)
        ttk.Button(f, text="Apply Theme", command=lambda: self.apply_theme(theme_combo.get())).pack(pady=5)

    def show_user_mgmt(self):
        # Admin only: Add/Delete users
        self.clear_main_area()
        
        tb = ttk.Frame(self.main_area)
        tb.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(tb, text="➕ Create User", command=self.create_user_dialog).pack(side=tk.LEFT)
        ttk.Button(tb, text="🗑️ Delete Selected User", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        cols = ["Username", "Role", "Last Login"]
        self.user_tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            self.user_tree.heading(c, text=c)
            self.user_tree.column(c, width=150)
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.load_users()

    def load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username, role, last_login FROM users")
        for r in c.fetchall():
            self.user_tree.insert("", tk.END, values=(r['username'], r['role'], r['last_login']))
        conn.close()

    def create_user_dialog(self):
        win = tk.Toplevel(self)
        win.geometry("300x200")
        win.title("Create User")
        win.transient(self)
        win.grab_set()
        
        f = ttk.Frame(win, padding=20)
        f.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(f, text="Username:").grid(row=0, column=0, sticky='w')
        u_entry = ttk.Entry(f)
        u_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Password:").grid(row=1, column=0, sticky='w')
        p_entry = ttk.Entry(f, show="*")
        p_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(f, text="Role:").grid(row=2, column=0, sticky='w')
        r_combo = ttk.Combobox(f, values=["admin", "user"])
        r_combo.current(1)
        r_combo.grid(row=2, column=1, sticky='ew', pady=5)
        
        def save():
            username = u_entry.get().strip()
            password = p_entry.get().strip()
            role = r_combo.get().strip()
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
            conn = get_db_connection()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, self.hash_pass(password), role))
                conn.commit()
                conn.close()
                log_action(self.current_user, "CREATE_USER", f"Created user {username}")
                messagebox.showinfo("Success", "User created successfully")
                win.destroy()
                self.load_users()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
                conn.close()
        
        ttk.Button(f, text="Create", command=save).grid(row=3, column=1, pady=10)

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            return
        username = self.user_tree.item(selected[0])['values'][0]
        if username == self.current_user:
            messagebox.showerror("Error", "Cannot delete your own account")
            return
        if messagebox.askyesno("Confirm", f"Delete user '{username}'?"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()
            log_action(self.current_user, "DELETE_USER", f"Deleted user {username}")
            self.load_users()

    def show_logs(self):
        self.clear_main_area()
        cols = ["ID", "User", "Action", "Details", "Timestamp"]
        tree = ttk.Treeview(self.main_area, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 500")
        for r in c.fetchall():
            tree.insert("", tk.END, values=(r['id'], r['user'], r['action'], r['details'], r['timestamp']))
        conn.close()

    # ----------------------
    # UTILITIES
    # ----------------------
    def clear_main_area(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(self.theme)

    def apply_theme(self, theme):
        if theme.lower() == "dark":
            self.configure(bg="#2c3e50")
            self.style.configure("TFrame", background="#2c3e50")
            self.style.configure("TLabel", background="#2c3e50", foreground="white")
            self.style.configure("Treeview", background="#34495e", foreground="white", fieldbackground="#34495e")
            self.style.configure("Treeview.Heading", background="#2c3e50", foreground="white")
        else:
            self.configure(bg="#ecf0f1")
            self.style.configure("TFrame", background="#ecf0f1")
            self.style.configure("TLabel", background="#ecf0f1", foreground="black")
            self.style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            self.style.configure("Treeview.Heading", background="#ecf0f1", foreground="black")
        log_action(self.current_user, "CHANGE_THEME", theme)

    def backup_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".sqlite", filetypes=[("SQLite DB", "*.sqlite")])
        if path:
            try:
                shutil.copy(DB_FILE, path)
                messagebox.showinfo("Success", "Database backed up successfully!")
                log_action(self.current_user, "BACKUP", f"Backup saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.sqlite;*.db"), ("All files", "*")])
        if not path:
            return

        if messagebox.askyesno("Confirm", "Restore the database from selected backup? This will replace current data."):
            try:
                shutil.copy2(path, DB_FILE)
                messagebox.showinfo("Success", "Database restored successfully. Restart the application to apply changes.")
                log_action(self.current_user, "RESTORE_DB", f"Restored database from {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Delete all audit logs? This action cannot be undone."):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM audit_logs")
            conn.commit()
            conn.close()
            log_action(self.current_user, "CLEAR_LOGS", "All logs cleared")
            messagebox.showinfo("Success", "All logs cleared")

    def export_students_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM students")
            rows = c.fetchall()
            conn.close()
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if rows:
                    writer.writerow(rows[0].keys())
                    for r in rows:
                        writer.writerow(r)
            messagebox.showinfo("Done", f"Exported {len(rows)} students to {path}")
            log_action(self.current_user, "EXPORT_STUDENTS", f"Exported to {path}")

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def logout(self):
        log_action(self.current_user, "LOGOUT", "User logged out")
        self.destroy()
        # Re-show login window (restart app)
        os.execl(sys.executable, sys.executable, *sys.argv)  # Restart the app

    def on_close_main(self):
        self.destroy()

# ==========================================
# NOTIFICATION SYSTEM FUNCTIONS
# ==========================================

def create_notification(title, message, notif_type, priority='normal', recipient_type='all', recipient_id=None, created_by='system', expires_days=30):
    """Create a new notification"""
    conn = get_db_connection()
    try:
        # Calculate expiration date
        expires_at = None
        if expires_days:
            expires_at = (datetime.datetime.now() + datetime.timedelta(days=expires_days)).strftime('%Y-%m-%d %H:%M:%S')

        # Insert notification
        cursor = conn.execute('''
            INSERT INTO notifications (title, message, type, priority, recipient_type, recipient_id, created_by, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, message, notif_type, priority, recipient_type, recipient_id, created_by, expires_at))

        notification_id = cursor.lastrowid

        # Create recipients based on type
        if recipient_type == 'all':
            # Get all users
            users = conn.execute('SELECT username FROM users').fetchall()
            for user in users:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, user[0]))
        elif recipient_type == 'student':
            # Get all students
            students = conn.execute('SELECT student_id FROM students').fetchall()
            for student in students:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, student[0]))
        elif recipient_type == 'admin':
            # Get all admins
            admins = conn.execute("SELECT username FROM users WHERE role = 'admin'").fetchall()
            for admin in admins:
                conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                           (notification_id, admin[0]))
        elif recipient_type == 'specific_student':
            # Specific student
            conn.execute('INSERT INTO notification_recipients (notification_id, recipient_id) VALUES (?, ?)',
                       (notification_id, recipient_id))

        conn.commit()
        return notification_id

    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None
    finally:
        conn.close()

def generate_payment_reminders():
    """Generate payment reminder notifications for upcoming due dates"""
    conn = get_db_connection()
    try:
        # Get payments due in the next 7 days
        seven_days_from_now = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')

        due_payments = conn.execute('''
            SELECT p.student_id, s.name, pc.name as category_name, p.due_date, p.amount
            FROM payments p
            JOIN students s ON p.student_id = s.student_id
            JOIN payment_categories pc ON p.category_id = pc.id
            WHERE p.status = 'Pending'
                AND p.due_date <= ?
                AND p.due_date >= date('now')
        ''', (seven_days_from_now,)).fetchall()

        for payment in due_payments:
            student_id, student_name, category_name, due_date, amount = payment

            title = f"Payment Reminder: {category_name} Due Soon"
            message = f"Dear {student_name},\n\nThis is a reminder that your {category_name} payment of ${amount:.2f} is due on {due_date}.\n\nPlease make your payment to avoid late fees.\n\nThank you!"

            create_notification(title, message, 'payment', 'high', 'specific_student', student_id, 'system', 7)

    except Exception as e:
        print(f"Error generating payment reminders: {str(e)}")
    finally:
        conn.close()

def generate_overdue_notifications():
    """Generate notifications for overdue payments"""
    conn = get_db_connection()
    try:
        # Get overdue payments
        overdue_payments = conn.execute('''
            SELECT p.student_id, s.name, pc.name as category_name, p.due_date, p.amount,
                   julianday('now') - julianday(p.due_date) as days_overdue
            FROM payments p
            JOIN students s ON p.student_id = s.student_id
            JOIN payment_categories pc ON p.category_id = pc.id
            WHERE p.status = 'Pending'
                AND p.due_date < date('now')
        ''').fetchall()

        for payment in overdue_payments:
            student_id, student_name, category_name, due_date, amount, days_overdue = payment

            title = f"OVERDUE: {category_name} Payment"
            message = f"Dear {student_name},\n\nYour {category_name} payment of ${amount:.2f} was due on {due_date} and is now {int(days_overdue)} days overdue.\n\nPlease contact the administration office immediately to make your payment and avoid further penalties.\n\nThank you!"

            create_notification(title, message, 'payment', 'urgent', 'specific_student', student_id, 'system', 30)

    except Exception as e:
        print(f"Error generating overdue notifications: {str(e)}")
    finally:
        conn.close()

def generate_grade_notifications(student_id, assessment_name, grade, subject):
    """Generate notification when a grade is posted"""
    conn = get_db_connection()
    try:
        student = conn.execute('SELECT name FROM students WHERE student_id = ?', (student_id,)).fetchone()
        if student:
            student_name = student[0]

            title = f"New Grade Posted: {subject} - {assessment_name}"
            message = f"Dear {student_name},\n\nA new grade has been posted for {subject}.\n\nAssessment: {assessment_name}\nGrade: {grade}\n\nPlease check your gradebook for detailed information.\n\nBest regards,\nAcademic Office"

            create_notification(title, message, 'grade', 'normal', 'specific_student', student_id, 'system', 30)

    except Exception as e:
        print(f"Error generating grade notification: {str(e)}")
    finally:
        conn.close()

def generate_attendance_warnings():
    """Generate warnings for students with low attendance"""
    conn = get_db_connection()
    try:
        # Get students with attendance below 75% in the last 30 days
        thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

        low_attendance = conn.execute('''
            SELECT s.student_id, s.name,
                   COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0 / COUNT(*) as attendance_rate
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date >= ?
            GROUP BY s.student_id, s.name
            HAVING attendance_rate < 75 AND COUNT(a.id) > 0
        ''', (thirty_days_ago,)).fetchall()

        for student in low_attendance:
            student_id, student_name, attendance_rate = student

            title = "Attendance Warning"
            message = f"Dear {student_name},\n\nYour attendance rate for the past 30 days is {attendance_rate:.1f}%, which is below the required 75%.\n\nPlease improve your attendance to avoid academic penalties.\n\nIf you have any concerns, please contact your teachers or the administration office.\n\nBest regards,\nAttendance Office"

            create_notification(title, message, 'attendance', 'high', 'specific_student', student_id, 'system', 30)

    except Exception as e:
        print(f"Error generating attendance warnings: {str(e)}")
    finally:
        conn.close()

def generate_report_card_notifications(student_id, academic_year, semester, gpa):
    """Generate notification when report card is ready"""
    conn = get_db_connection()
    try:
        student = conn.execute('SELECT name FROM students WHERE student_id = ?', (student_id,)).fetchone()
        if student:
            student_name = student[0]

            title = f"Report Card Ready: {academic_year} {semester}"
            message = f"Dear {student_name},\n\nYour report card for {academic_year} {semester} is now ready.\n\nGPA: {gpa:.2f}\n\nPlease collect your report card from the administration office or check the gradebook section for details.\n\nCongratulations on your academic achievements!\n\nBest regards,\nAcademic Office"

            create_notification(title, message, 'report_card_ready', 'normal', 'specific_student', student_id, 'system', 90)

    except Exception as e:
        print(f"Error generating report card notification: {str(e)}")
    finally:
        conn.close()

def check_and_generate_notifications():
    """Check for events that require notifications and generate them"""
    try:
        # Generate payment reminders
        generate_payment_reminders()

        # Generate overdue payment notifications
        generate_overdue_notifications()

        # Generate attendance warnings
        generate_attendance_warnings()

        print("✅ Notification check completed")

    except Exception as e:
        print(f"Error in notification check: {str(e)}")

    # ==========================================
    # PARENT PORTAL METHODS
    # ==========================================

    def get_parent_children(self):
        """Get list of children for the current parent user"""
        conn = get_db_connection()
        try:
            children = conn.execute('''
                SELECT s.student_id, s.name, s.program, s.enrollment_date, ps.relationship,
                       ps.can_view_grades, ps.can_view_payments, ps.can_view_attendance
                FROM parent_students ps
                JOIN students s ON ps.student_id = s.student_id
                WHERE ps.parent_user_id = ?
                ORDER BY s.name
            ''', (self.current_user_id,)).fetchall()
            return children
        finally:
            conn.close()

    def show_parent_dashboard(self):
        """Show parent dashboard with overview of all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="🏠 Parent Dashboard", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Children Overview
        overview_frame = ttk.Frame(self.main_area)
        overview_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(overview_frame, text=f"You have {len(children)} child(ren) enrolled:", font=('Segoe UI', 14, 'bold')).pack(anchor='w')

        # Children cards
        children_frame = ttk.Frame(self.main_area)
        children_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for i, child in enumerate(children):
            child_frame = ttk.LabelFrame(children_frame, text=f"{child['name']} ({child['relationship']})", padding=10)
            child_frame.pack(fill=tk.X, pady=5)

            # Child info
            info_frame = ttk.Frame(child_frame)
            info_frame.pack(fill=tk.X)

            ttk.Label(info_frame, text=f"Student ID: {child['student_id']}", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', padx=5)
            ttk.Label(info_frame, text=f"Program: {child['program']}", font=('Segoe UI', 10)).grid(row=0, column=1, sticky='w', padx=5)
            ttk.Label(info_frame, text=f"Enrolled: {child['enrollment_date']}", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', padx=5)

            # Quick stats
            stats_frame = ttk.Frame(child_frame)
            stats_frame.pack(fill=tk.X, pady=5)

            # Get quick stats for this child
            conn = get_db_connection()
            try:
                # GPA
                gpa_result = conn.execute('''
                    SELECT AVG(marks) as gpa FROM subjects WHERE student_id = ?
                ''', (child['student_id'],)).fetchone()
                gpa = round(gpa_result['gpa'], 2) if gpa_result['gpa'] else 0

                # Attendance
                attendance_result = conn.execute('''
                    SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
                    FROM attendance WHERE student_id = ?
                ''', (child['student_id'],)).fetchone()
                attendance_rate = (attendance_result['present'] / attendance_result['total'] * 100) if attendance_result['total'] > 0 else 0

                # Payments
                payment_result = conn.execute('''
                    SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END) as paid
                    FROM payments WHERE student_id = ?
                ''', (child['student_id'],)).fetchone()
                payment_completion = (payment_result['paid'] / payment_result['total'] * 100) if payment_result['total'] > 0 else 100

            finally:
                conn.close()

            ttk.Label(stats_frame, text=f"GPA: {gpa}", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=10)
            ttk.Label(stats_frame, text=f"Attendance: {attendance_rate:.1f}%", font=('Segoe UI', 10, 'bold')).grid(row=0, column=1, padx=10)
            ttk.Label(stats_frame, text=f"Payments: {payment_completion:.1f}%", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, padx=10)

    def show_parent_children(self):
        """Show detailed view of all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="👨‍👩‍👧‍👦 My Children", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Children list
        tree_frame = ttk.Frame(self.main_area)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('Student ID', 'Name', 'Program', 'Enrollment Date', 'Relationship')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate tree
        for child in children:
            tree.insert('', tk.END, values=(
                child['student_id'],
                child['name'],
                child['program'],
                child['enrollment_date'],
                child['relationship']
            ))

        # Action buttons
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(btn_frame, text="View Details", command=lambda: self.view_child_details(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Academic Progress", command=lambda: self.show_parent_grades()).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Payment Status", command=lambda: self.show_parent_payments()).pack(side=tk.LEFT, padx=5)

    def view_child_details(self, tree):
        """View detailed information about a selected child"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a child to view details.")
            return

        item = tree.item(selected[0])
        student_id = item['values'][0]

        # Get detailed student info
        conn = get_db_connection()
        try:
            student = conn.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()
        finally:
            conn.close()

        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        # Show details window
        details_win = tk.Toplevel(self)
        details_win.title(f"Student Details - {student['name']}")
        details_win.geometry("600x500")

        # Student photo (if available)
        if student['image_path'] and os.path.exists(student['image_path']):
            try:
                from PIL import Image, ImageTk
                img = Image.open(student['image_path'])
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                ttk.Label(details_win, image=photo).pack(pady=10)
                details_win.photo = photo  # Keep reference
            except:
                pass

        # Details
        details_frame = ttk.Frame(details_win, padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(details_frame, text=f"Name: {student['name']}", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Student ID: {student['student_id']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Email: {student['email'] or 'Not provided'}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Phone: {student['phone'] or 'Not provided'}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Program: {student['program']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Gender: {student['gender']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Date of Birth: {student['dob']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Address: {student['address']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Guardian: {student['guardian_name']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Guardian Phone: {student['guardian_phone']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Enrollment Date: {student['enrollment_date']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Status: {student['status']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)

    def show_parent_grades(self):
        """Show academic progress for all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="📊 Academic Progress", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Create notebook for each child
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for child in children:
            if not child['can_view_grades']:
                continue

            # Create tab for this child
            child_frame = ttk.Frame(notebook)
            notebook.add(child_frame, text=child['name'])

            # Get grades for this child
            conn = get_db_connection()
            try:
                grades = conn.execute('''
                    SELECT subject_name, marks, credits, semester
                    FROM subjects
                    WHERE student_id = ?
                    ORDER BY semester, subject_name
                ''', (child['student_id'],)).fetchall()

                # GPA calculation
                if grades:
                    total_points = sum(grade['marks'] * grade['credits'] for grade in grades)
                    total_credits = sum(grade['credits'] for grade in grades)
                    gpa = total_points / total_credits if total_credits > 0 else 0
                else:
                    gpa = 0

            finally:
                conn.close()

            # GPA Display
            ttk.Label(child_frame, text=f"Current GPA: {gpa:.2f}", font=('Segoe UI', 14, 'bold')).pack(pady=10)

            # Grades table
            tree_frame = ttk.Frame(child_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            columns = ('Subject', 'Marks', 'Credits', 'Grade', 'Semester')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate grades
            for grade in grades:
                grade_letter = self.calculate_grade_letter(grade['marks'])
                tree.insert('', tk.END, values=(
                    grade['subject_name'],
                    f"{grade['marks']:.1f}",
                    grade['credits'],
                    grade_letter,
                    grade['semester']
                ))

    def calculate_grade_letter(self, marks):
        """Convert marks to grade letter"""
        if marks >= 90: return 'A+'
        elif marks >= 85: return 'A'
        elif marks >= 80: return 'A-'
        elif marks >= 75: return 'B+'
        elif marks >= 70: return 'B'
        elif marks >= 65: return 'B-'
        elif marks >= 60: return 'C+'
        elif marks >= 55: return 'C'
        elif marks >= 50: return 'C-'
        elif marks >= 45: return 'D'
        else: return 'F'

    def show_parent_payments(self):
        """Show payment status for all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="💰 Payment Status", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Create notebook for each child
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for child in children:
            if not child['can_view_payments']:
                continue

            # Create tab for this child
            child_frame = ttk.Frame(notebook)
            notebook.add(child_frame, text=child['name'])

            # Get payments for this child
            conn = get_db_connection()
            try:
                payments = conn.execute('''
                    SELECT p.id, pc.name as category, p.amount, p.payment_date, p.due_date,
                           p.payment_method, p.status, p.notes
                    FROM payments p
                    JOIN payment_categories pc ON p.category_id = pc.id
                    WHERE p.student_id = ?
                    ORDER BY p.due_date DESC
                ''', (child['student_id'],)).fetchall()

                # Payment summary
                total_due = sum(p['amount'] for p in payments if p['status'] != 'Paid')
                total_paid = sum(p['amount'] for p in payments if p['status'] == 'Paid')

            finally:
                conn.close()

            # Summary
            summary_frame = ttk.Frame(child_frame)
            summary_frame.pack(fill=tk.X, pady=10)

            ttk.Label(summary_frame, text=f"Total Paid: ${total_paid:.2f}", font=('Segoe UI', 12, 'bold'),
                     foreground="green").grid(row=0, column=0, padx=10)
            ttk.Label(summary_frame, text=f"Outstanding: ${total_due:.2f}", font=('Segoe UI', 12, 'bold'),
                     foreground="red").grid(row=0, column=1, padx=10)

            # Payments table
            tree_frame = ttk.Frame(child_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            columns = ('Category', 'Amount', 'Due Date', 'Payment Date', 'Method', 'Status')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate payments
            for payment in payments:
                tree.insert('', tk.END, values=(
                    payment['category'],
                    f"${payment['amount']:.2f}",
                    payment['due_date'] or 'N/A',
                    payment['payment_date'] or 'N/A',
                    payment['payment_method'] or 'N/A',
                    payment['status']
                ))

    def show_parent_attendance(self):
        """Show attendance records for all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="📅 Attendance Records", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Create notebook for each child
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for child in children:
            if not child['can_view_attendance']:
                continue

            # Create tab for this child
            child_frame = ttk.Frame(notebook)
            notebook.add(child_frame, text=child['name'])

            # Get attendance for this child
            conn = get_db_connection()
            try:
                attendance = conn.execute('''
                    SELECT date, status, remarks
                    FROM attendance
                    WHERE student_id = ?
                    ORDER BY date DESC
                    LIMIT 50
                ''', (child['student_id'],)).fetchall()

                # Attendance summary
                total_days = len(attendance)
                present_days = sum(1 for a in attendance if a['status'] == 'Present')
                attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

            finally:
                conn.close()

            # Summary
            ttk.Label(child_frame, text=f"Attendance Rate: {attendance_rate:.1f}% ({present_days}/{total_days} days)",
                     font=('Segoe UI', 14, 'bold')).pack(pady=10)

            # Attendance table
            tree_frame = ttk.Frame(child_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            columns = ('Date', 'Status', 'Remarks')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate attendance
            for record in attendance:
                tree.insert('', tk.END, values=(
                    record['date'],
                    record['status'],
                    record['remarks'] or ''
                ))

    def show_parent_reports(self):
        """Show report cards for all children"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="📄 Report Cards", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Get children
        children = self.get_parent_children()

        if not children:
            ttk.Label(self.main_area, text="No children linked to your account.\nPlease contact the administrator to link your children.",
                     font=('Segoe UI', 12)).pack(pady=50)
            return

        # Create notebook for each child
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for child in children:
            # Create tab for this child
            child_frame = ttk.Frame(notebook)
            notebook.add(child_frame, text=child['name'])

            # Get report cards for this child
            conn = get_db_connection()
            try:
                reports = conn.execute('''
                    SELECT rc.id, ay.year_name, rc.semester, rc.gpa, rc.status, rc.generated_at
                    FROM report_cards rc
                    JOIN academic_years ay ON rc.academic_year_id = ay.id
                    WHERE rc.student_id = ?
                    ORDER BY rc.generated_at DESC
                ''', (child['student_id'],)).fetchall()

            finally:
                conn.close()

            if not reports:
                ttk.Label(child_frame, text="No report cards available yet.", font=('Segoe UI', 12)).pack(pady=50)
                continue

            # Report cards list
            tree_frame = ttk.Frame(child_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            columns = ('Academic Year', 'Semester', 'GPA', 'Status', 'Generated Date')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate report cards
            for report in reports:
                tree.insert('', tk.END, values=(
                    report['year_name'],
                    report['semester'],
                    f"{report['gpa']:.2f}" if report['gpa'] else 'N/A',
                    report['status'],
                    report['generated_at'][:10] if report['generated_at'] else 'N/A'
                ))

            # Action buttons
            btn_frame = ttk.Frame(child_frame)
            btn_frame.pack(fill=tk.X, pady=10)

            ttk.Button(btn_frame, text="View Details", command=lambda t=tree: self.view_report_details(t)).pack(side=tk.LEFT, padx=5)

    def view_report_details(self, tree):
        """View detailed report card information"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a report card to view.")
            return

        item = tree.item(selected[0])
        # Note: We don't have the report_id in the tree values, so we'd need to modify this
        # For now, just show a placeholder
        messagebox.showinfo("Report Card", "Detailed report card view would be implemented here.\nThis would show subject-wise grades, comments, and overall performance.")

    def show_parent_notifications(self):
        """Show notifications for parent (same as regular notifications but filtered)"""
        self.show_notifications()

    def show_parent_messages(self):
        """Show messaging system for parents to communicate with admins"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="💬 Messages", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Create notebook for inbox and compose
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Inbox tab
        inbox_frame = ttk.Frame(notebook)
        notebook.add(inbox_frame, text="Inbox")

        # Messages list
        tree_frame = ttk.Frame(inbox_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('Subject', 'From', 'Type', 'Status', 'Date')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load messages
        self.load_parent_messages(tree)

        # Action buttons
        btn_frame = ttk.Frame(inbox_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="View Message", command=lambda: self.view_parent_message(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Mark as Read", command=lambda: self.mark_message_read(tree)).pack(side=tk.LEFT, padx=5)

        # Compose tab
        compose_frame = ttk.Frame(notebook)
        notebook.add(compose_frame, text="Compose")

        # Compose form
        form_frame = ttk.Frame(compose_frame, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Subject:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        subject_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=subject_var).grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(form_frame, text="Message Type:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        type_var = tk.StringVar(value="general")
        ttk.Combobox(form_frame, textvariable=type_var, values=["general", "complaint", "inquiry", "praise"]).grid(row=1, column=1, sticky='ew', pady=5)

        ttk.Label(form_frame, text="Priority:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        priority_var = tk.StringVar(value="normal")
        ttk.Combobox(form_frame, textvariable=priority_var, values=["low", "normal", "high", "urgent"]).grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(form_frame, text="Related Child (optional):", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        child_var = tk.StringVar()
        children = self.get_parent_children()
        child_options = ["None"] + [f"{c['name']} ({c['student_id']})" for c in children]
        ttk.Combobox(form_frame, textvariable=child_var, values=child_options).grid(row=3, column=1, sticky='ew', pady=5)

        ttk.Label(form_frame, text="Message:", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        message_text = tk.Text(form_frame, height=10, width=50)
        message_text.grid(row=4, column=1, sticky='ew', pady=5)

        form_frame.columnconfigure(1, weight=1)

        ttk.Button(form_frame, text="Send Message",
                  command=lambda: self.send_parent_message(subject_var.get(), message_text.get("1.0", tk.END).strip(),
                                                         type_var.get(), priority_var.get(), child_var.get())).grid(row=5, column=0, columnspan=2, pady=20)

    def load_parent_messages(self, tree):
        """Load messages for the current parent"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        conn = get_db_connection()
        try:
            messages = conn.execute('''
                SELECT pm.id, pm.subject, u.username as from_user, pm.message_type,
                       pm.status, pm.created_at, s.name as student_name
                FROM parent_messages pm
                LEFT JOIN users u ON pm.from_user_id = u.id
                LEFT JOIN students s ON pm.student_id = s.student_id
                WHERE pm.from_user_id = ? OR pm.to_user_id = ?
                ORDER BY pm.created_at DESC
            ''', (self.current_user_id, self.current_user_id)).fetchall()

            for msg in messages:
                from_user = msg['from_user'] if msg['from_user'] != self.current_user else "You"
                tree.insert('', tk.END, values=(
                    msg['subject'],
                    from_user,
                    msg['message_type'],
                    msg['status'],
                    msg['created_at'][:10]
                ))

        finally:
            conn.close()

    def view_parent_message(self, tree):
        """View selected message details"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a message to view.")
            return

        # This would need to be implemented to show full message details
        messagebox.showinfo("Message View", "Full message viewing would be implemented here.")

    def mark_message_read(self, tree):
        """Mark selected message as read"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a message to mark as read.")
            return

        # This would need to be implemented to update message status
        messagebox.showinfo("Mark as Read", "Message marking functionality would be implemented here.")

    def send_parent_message(self, subject, message, msg_type, priority, child_info):
        """Send a message from parent to admin"""
        if not subject or not message:
            messagebox.showerror("Error", "Subject and message are required.")
            return

        # Parse child info
        student_id = None
        if child_info and child_info != "None":
            # Extract student_id from format "Name (STUDENT_ID)"
            try:
                student_id = child_info.split('(')[-1].rstrip(')')
            except:
                pass

        conn = get_db_connection()
        try:
            # Find admin user (assuming there's at least one admin)
            admin = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
            if not admin:
                messagebox.showerror("Error", "No administrator found to send message to.")
                return

            conn.execute('''
                INSERT INTO parent_messages (from_user_id, to_user_id, student_id, subject, message, message_type, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_user_id, admin['id'], student_id, subject, message, msg_type, priority))

            conn.commit()
            messagebox.showinfo("Success", "Message sent successfully!")
            # Refresh messages would be called here

        finally:
            conn.close()

    def show_parent_settings(self):
        """Show parent-specific settings"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_area, text="⚙️ Parent Settings", font=('Segoe UI', 20, 'bold')).pack(pady=20)

        # Settings frame
        settings_frame = ttk.Frame(self.main_area, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(settings_frame, text="Notification Preferences", font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=10)

        # Notification settings for parent
        notification_types = [
            ('grade_posted', 'Grade Posted'),
            ('payment_reminder', 'Payment Reminders'),
            ('payment_overdue', 'Overdue Payments'),
            ('attendance_warning', 'Attendance Warnings'),
            ('report_card_ready', 'Report Card Ready'),
            ('system_announcement', 'System Announcements')
        ]

        for notif_type, display_name in notification_types:
            frame = ttk.Frame(settings_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=display_name).pack(side=tk.LEFT)
            ttk.Checkbutton(frame, text="In-App").pack(side=tk.RIGHT, padx=10)
            ttk.Checkbutton(frame, text="Email").pack(side=tk.RIGHT, padx=10)
            ttk.Checkbutton(frame, text="SMS").pack(side=tk.RIGHT, padx=10)

        # Account settings
        ttk.Label(settings_frame, text="Account Settings", font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=20)

        ttk.Button(settings_frame, text="Change Password", command=self.change_parent_password).pack(anchor='w', pady=5)
        ttk.Button(settings_frame, text="Contact Information", command=self.update_parent_contact).pack(anchor='w', pady=5)

    def change_parent_password(self):
        """Allow parent to change their password"""
        # Simple password change dialog
        current_pass = simpledialog.askstring("Change Password", "Enter current password:", show="*")
        if not current_pass:
            return

        new_pass = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if not new_pass:
            return

        confirm_pass = simpledialog.askstring("Change Password", "Confirm new password:", show="*")
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Verify current password and update
        conn = get_db_connection()
        try:
            user = conn.execute("SELECT password FROM users WHERE id = ?", (self.current_user_id,)).fetchone()
            if user and user['password'] == self.hash_pass(current_pass):
                conn.execute("UPDATE users SET password = ? WHERE id = ?", (self.hash_pass(new_pass), self.current_user_id))
                conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!")
            else:
                messagebox.showerror("Error", "Current password is incorrect.")
        finally:
            conn.close()

    def update_parent_contact(self):
        """Allow parent to update their contact information"""
        # This would show a form to update contact details
        messagebox.showinfo("Contact Information", "Contact information update would be implemented here.")

if __name__ == "__main__":
    app = ProStudentApp()
    app.mainloop()