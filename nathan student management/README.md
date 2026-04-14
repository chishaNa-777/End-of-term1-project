student_number: 2025558145
Name: Nathan Sichilima
# Ultimate Student Management System Pro v3.0

A comprehensive desktop application for managing student information, built with Python and Tkinter. This system provides a complete solution for educational institutions to track students, their academic performance, attendance, and more.

## Features

### Core Functionality
- **User Authentication**: Secure login system with role-based access (Admin/User)
- **Student Management**: Add, edit, delete, and search student records
- **Payment Tracking**: Complete fee management system with categories, methods, and reporting
- **🔔 Notification System**: Automated notifications for payments, grades, attendance, and announcements
- **Gradebook System**: Advanced grade entry, GPA calculation, and assessment management
- **Report Cards**: Automated report card generation with academic summaries
- **Academic Tracking**: Manage subjects, marks, and grades
- **Tutorial System**: Watch educational videos and tutorials
- **Study Materials**: Access and download lecture notes and study materials
- **Attendance System**: Mark and track student attendance
- **Analytics Dashboard**: Visual charts and performance analytics
- **Audit Logging**: Track all system activities for security

### Student Information
- Personal details (name, email, phone, address, DOB)
- Academic program and enrollment information
- Guardian contact details
- Student photos upload and viewing (admin only)
- Status tracking (Active/Inactive)

### Academic Features
- Subject-wise marks entry and grading
- GPA calculation
- Semester-based organization
- Grade classification (A+, A, B+, etc.)

### Administrative Tools
- User management (admin only)
- Tutorial management: Upload and manage educational videos
- Study materials management: Upload and manage lecture notes
- System settings and configuration
- Database backup and export
- Theme switching (Light/Dark)
- CSV export functionality

### Analytics & Reporting
- Pass/Fail ratio charts
- Program distribution statistics
- Top performers list
- Attendance summaries
- Recent activity logs

## 🔔 Notification System

The comprehensive notification system provides automated communication for important events and announcements.

### Features
- **Automated Notifications**: Automatically generated for payments, grades, attendance, and report cards
- **Multi-Recipient Support**: Send to all users, specific students, or groups
- **Priority Levels**: Normal, High, and Urgent priority notifications
- **Notification Types**: System announcements, payment reminders, grade alerts, attendance warnings, report cards
- **Expiry Management**: Notifications can have expiration dates
- **Read/Unread Tracking**: Track which notifications have been read by recipients
- **Settings Management**: Configure notification preferences (in-app, email, SMS)
- **Multi-Channel Support**: Currently supports in-app notifications, with email/SMS ready for implementation

### Notification Types
- **System Announcements**: Important updates and news from administrators
- **Payment Reminders**: Due date notifications and overdue alerts
- **Grade Notifications**: When grades are posted or updated
- **Attendance Warnings**: Low attendance alerts
- **Report Card Ready**: When report cards are available for download
- **GPA Updates**: When GPA calculations are updated

### User Interface
- **Four-Tab Interface**: All, Unread, Create, Settings tabs
- **Notification List**: View all notifications with filtering options
- **Create Notifications**: Admin interface for creating custom notifications
- **Settings Panel**: Configure notification preferences
- **Unread Badge**: Shows count of unread notifications in sidebar

### Automated Triggers
- Payment due dates (7 days before)
- Grade posting
- Low attendance (3+ missed classes)
- Report card generation
- GPA updates
- System maintenance announcements

## Requirements

### System Requirements
- Python 3.6 or higher
- Windows/Linux/macOS

### Python Dependencies
- tkinter (usually included with Python)
- sqlite3 (included with Python)
- matplotlib (optional, for charts)
- hashlib, csv, os, sys, random, datetime, shutil, collections (all standard library)

### Optional Dependencies
- matplotlib: For generating visual charts in the analytics section
  ```bash
  pip install matplotlib
  ```

## Installation

1. **Clone or Download**: Place the `student_managemnt.py` file in your desired directory.

2. **Install Dependencies** (if matplotlib is desired):
   ```bash
   pip install matplotlib
   ```

3. **Run the Application**:
   ```bash
   python student_managemnt.py
   ```

The application will automatically create the SQLite database (`student_db.sqlite`) on first run.

## Usage

### First Time Setup
- Launch the application
- Login with default admin credentials:
  - Username: `admin`
  - Password: `admin123`

### Navigation
- Use the sidebar to navigate between different sections
- Dashboard: Overview of system statistics
- Students: Manage student records
- Payment Tracking: Manage fees and payments
- Gradebook: Advanced grade management and GPA calculation
- Subjects & Marks: Enter and view academic performance
- Tutorials: Watch educational videos
- Study Notes: Access lecture notes and study materials
- Attendance: Track daily attendance
- Analytics: View charts and reports
- Settings: System configuration and tools

## 🔔 Using the Notification System

### Accessing Notifications
1. Click the **"🔔 Notifications"** button in the sidebar
2. The notification center will open with four tabs

### Viewing Notifications
- **All Tab**: View all notifications (read and unread)
- **Unread Tab**: View only unread notifications
- Use the treeview to see notification details
- Double-click a notification to mark it as read

### Creating Notifications (Admin Only)
1. Go to the **"Create"** tab
2. Fill in the notification details:
   - Title and message
   - Type (system, payment, grade, attendance, report)
   - Priority (normal, high, urgent)
   - Recipient type (all users or specific student)
   - Expiry days (optional)
3. Click "Create Notification"

### Notification Settings
1. Go to the **"Settings"** tab
2. Configure preferences for each notification type:
   - In-app notifications (currently active)
   - Email notifications (ready for implementation)
   - SMS notifications (ready for implementation)

### Automated Notifications
The system automatically creates notifications for:
- **Payment Reminders**: 7 days before due dates
- **Grade Posting**: When grades are entered
- **Attendance Warnings**: When students miss 3+ classes
- **Report Cards**: When report cards are generated
- **GPA Updates**: When GPA calculations change

### Notification Badge
- The sidebar shows an unread count badge next to "🔔 Notifications"
- Badge updates automatically when notifications are read

## Payment Tracking System

The payment tracking system provides comprehensive fee management capabilities for educational institutions.

### Features
- **Payment Categories**: Pre-configured categories (Tuition, Registration, Library, etc.)
- **Custom Categories**: Add institution-specific payment types
- **Payment Methods**: Multiple payment options (Cash, Bank Transfer, Mobile Money, etc.)
- **Status Tracking**: Monitor payment status (Pending, Paid, Overdue, Cancelled)
- **Due Date Management**: Set and track payment deadlines
- **Reference Numbers**: Track payment receipts and transaction IDs
- **Financial Reporting**: Export detailed payment reports

### Default Payment Categories
- Tuition Fee ($5,000)
- Registration Fee ($500)
- Library Fee ($200)
- Laboratory Fee ($300)
- Sports Fee ($150)
- Transportation Fee ($400)
- Materials Fee ($250)
- Examination Fee ($100)

### Payment Methods
- Cash
- Bank Transfer
- Zanaco Bank
- Credit Card
- Debit Card
- Mobile Money
- Airtel Money
- Cheque
- Scholarship
- Installment

### Using Payment Tracking
1. **Record Payment**: Click "Record Payment" to add a new payment transaction
2. **Select Student**: Choose the student from the dropdown list
3. **Choose Category**: Select the payment type from available categories
4. **Enter Details**: Amount, due date, payment date, method, and reference
5. **Track Status**: Monitor payment status and outstanding fees
6. **Export Reports**: Generate CSV reports for accounting purposes

### Payment Dashboard
- **Summary Statistics**: Total pending, paid, and overdue amounts
- **Status Filtering**: Filter payments by status (All, Pending, Paid, Overdue, Cancelled)
- **Student Filtering**: View payments for specific students
- **Search Functionality**: Search payments by any field
- **Color Coding**: Visual indicators for payment status

## Notification System

The notification system provides automated communication for important events and announcements.

### Features
- **Automated Notifications**: System-generated notifications for payments, grades, and attendance
- **Custom Announcements**: Create custom notifications for all users or specific students
- **Priority Levels**: Normal, High, and Urgent priority notifications
- **Recipient Targeting**: Send to all users, students only, admins only, or specific students
- **Read Status Tracking**: Track which notifications have been read by recipients
- **Expiration Management**: Set expiration dates for time-sensitive notifications
- **Notification Badge**: Visual indicator showing unread notification count

### Notification Types
- **Payment Notifications**: Due date reminders, overdue warnings, payment confirmations
- **Grade Notifications**: New grade postings, GPA updates, report card availability
- **Attendance Notifications**: Low attendance warnings and alerts
- **System Announcements**: General announcements and important updates
- **Custom Notifications**: Administrator-created announcements

### Automatic Notifications
The system automatically generates notifications for:
- Payment reminders (7 days before due date)
- Overdue payment warnings
- New grade postings
- Low attendance alerts (< 75% in 30 days)
- Report card generation
- Payment confirmations

### Using the Notification System
1. **Access Notifications**: Click "Notifications" in the sidebar
2. **View Notifications**: Use tabs to view All, Unread, or create new notifications
3. **Create Announcements**: Use the "Create New" tab to send custom notifications
4. **Manage Notifications**: Mark as read, delete, or view notification details
5. **Configure Settings**: Adjust notification preferences in the Settings tab

### Notification Dashboard
- **Unread Badge**: Sidebar button shows count of unread notifications
- **Priority Indicators**: Visual indicators for different priority levels
- **Status Tracking**: See which notifications have been read
- **Search and Filter**: Find specific notifications quickly

## Gradebook & Report Cards System

The advanced gradebook system provides comprehensive academic assessment and reporting capabilities.

### Gradebook Features
- **Assessment Management**: Create and manage different types of assessments
- **Grade Categories**: Organize assessments by type (Assignments, Quizzes, Exams)
- **Weighted Grading**: Configure weights for different assessment types
- **Grade Entry**: Bulk grade entry for multiple students
- **GPA Calculation**: Automatic GPA calculation with customizable scales
- **Grade Analytics**: Detailed performance analytics and statistics

### Report Cards
- **Automated Generation**: Generate report cards with GPA and subject grades
- **Academic Years**: Manage multiple academic years and semesters
- **Subject Breakdown**: Detailed subject-wise performance
- **Progress Tracking**: Track academic progress over time
- **Certificate Generation**: Create completion certificates
- **Export Options**: Print and export report cards

### Assessment Types
- **Assignments**: Homework and project assignments
- **Quizzes**: Short quizzes and tests
- **Midterm Exams**: Midterm examinations
- **Final Exams**: Final examinations
- **Labs**: Laboratory work and practical assessments
- **Presentations**: Oral presentations and projects

### Grade Scale
- **A+ (90-100%)**: 4.0 GPA
- **A (85-89%)**: 3.7 GPA
- **A- (80-84%)**: 3.3 GPA
- **B+ (75-79%)**: 3.0 GPA
- **B (70-74%)**: 2.7 GPA
- **B- (65-69%)**: 2.3 GPA
- **C+ (60-64%)**: 2.0 GPA
- **C (55-59%)**: 1.7 GPA
- **C- (50-54%)**: 1.3 GPA
- **D (45-49%)**: 1.0 GPA
- **F (0-44%)**: 0.0 GPA

### Using the Gradebook
1. **Setup Assessments**: Go to "Assessment Setup" tab to create categories and assessments
2. **Enter Grades**: Use "Grade Entry" tab to record student grades
3. **Calculate GPA**: Use GPA calculator for individual student analysis
4. **View Analytics**: Check grade distributions and performance statistics
5. **Generate Reports**: Create report cards for academic periods

### Report Card Generation
1. **Select Student**: Choose student from dropdown
2. **Choose Academic Year**: Select the relevant academic year
3. **Set Semester**: Annual, Semester 1, or Semester 2
4. **Generate**: System calculates GPA and creates detailed report
5. **View/Print**: View report card details and print for distribution

### Academic Year Management
- **Multiple Years**: Support for multiple academic years
- **Current Year**: Mark current academic year
- **Semester Tracking**: Track different semesters
- **Progress Monitoring**: Monitor academic progress over time

The payment tracking system provides comprehensive fee management capabilities for educational institutions.

### Features
- **Payment Categories**: Pre-configured categories (Tuition, Registration, Library, etc.)
- **Custom Categories**: Add institution-specific payment types
- **Payment Methods**: Multiple payment options (Cash, Bank Transfer, Mobile Money, etc.)
- **Status Tracking**: Monitor payment status (Pending, Paid, Overdue, Cancelled)
- **Due Date Management**: Set and track payment deadlines
- **Reference Numbers**: Track payment references and receipts
- **Financial Reporting**: Export detailed payment reports

### Default Payment Categories
- Tuition Fee ($5,000)
- Registration Fee ($500)
- Library Fee ($200)
- Laboratory Fee ($300)
- Sports Fee ($150)
- Transportation Fee ($400)
- Materials Fee ($250)
- Examination Fee ($100)

### Payment Methods
- Cash
- Bank Transfer
- Credit Card
- Debit Card
- Mobile Money
- Cheque
- Scholarship
- Installment

### Using Payment Tracking
1. **Record Payment**: Click "Record Payment" to add a new payment transaction
2. **Select Student**: Choose the student from the dropdown list
3. **Choose Category**: Select the payment type from available categories
4. **Enter Details**: Amount, due date, payment date, method, and reference
5. **Track Status**: Monitor payment status and overdue amounts
6. **Export Reports**: Generate CSV reports for accounting purposes

### Payment Dashboard
- **Summary Statistics**: Total pending, paid, and overdue amounts
- **Status Filtering**: Filter payments by status (All, Pending, Paid, Overdue, Cancelled)
- **Student Filtering**: View payments for specific students
- **Search Functionality**: Search payments by any field
- **Color Coding**: Visual indicators for payment status

### Adding Students
1. Go to "Students" section
2. Click "Add Student"
3. Fill in all required fields
4. (Admin only) Upload a student photo by clicking "Browse" and selecting an image file
5. Click "Save"

### Viewing Student Photos
1. Select a student in the Students section
2. Click "View Photo" to open the student's photo (if available)

### Watching Tutorials
1. Go to "Tutorials" section
2. Select a tutorial from the list
3. Click "Watch Selected" to open the video in your default web browser

### Managing Tutorials (Admin Only)
1. Go to "Tutorials" section
2. Click "Add Tutorial"
3. Fill in title, subject, description, and video URL
4. Click "Save"

### Accessing Study Notes
1. Go to "Study Notes" section
2. Select notes from the list
3. Click "Download Selected" to open the file with your default application

### Uploading Study Notes (Admin Only)
1. Go to "Study Notes" section
2. Click "Upload Notes"
3. Enter title and subject
4. Click "Browse" to select a file (PDF, DOC, DOCX, TXT)
5. Click "Upload"

### Managing Academic Records
1. Navigate to "Subjects & Marks"
2. Click "Add Marks"
3. Select student, enter subject details and marks
4. Save the record

### Attendance Tracking
1. Go to "Attendance" section
2. Click "Mark Attendance (Today)"
3. Select date and mark status for each student
4. Save all attendance records

## Default Credentials

- **Admin User**:
  - Username: `admin`
  - Password: `chisha@123`

**Important**: Change the default password immediately after first login for security purposes.

## Database Structure

The application uses SQLite with the following tables:
- `users`: User accounts and authentication
- `students`: Student personal and academic information
- `subjects`: Academic subjects and marks
- `tutorials`: Educational video tutorials
- `study_notes`: Uploaded lecture notes and study materials
- `attendance`: Daily attendance records
- `audit_logs`: System activity logs
- `settings`: Application configuration

## Backup and Export

### Database Backup
- Go to Settings → "Backup Database to File"
- Choose save location for the backup file

### Export Data
- Students can be exported to CSV format
- Use the "Export CSV" button in the Students section

## Troubleshooting

### Common Issues

1. **Charts not displaying**
   - Install matplotlib: `pip install matplotlib`
   - Restart the application

2. **Database errors**
   - Ensure write permissions in the application directory
   - Check if `student_db.sqlite` is not corrupted

3. **Login issues**
   - Verify username and password
   - Check user role permissions

4. **Performance issues**
   - Clear audit logs periodically
   - Consider database optimization for large datasets

### Logs and Debugging
- View system logs in the "Logs" section (admin only)
- Check audit logs for recent activities
- Clear logs if database size becomes an issue

## Security Features

- Password hashing using SHA-256
- Role-based access control
- Audit logging for all actions
- Secure database storage

## 🧪 Testing & Demo Scripts

The system includes comprehensive testing and demonstration scripts to verify functionality and showcase features.

### Notification System Testing
```bash
# Run notification system database verification
python test_notifications.py
```
This script verifies:
- Database table creation and structure
- Notification settings initialization
- Function availability and basic operations

### Comprehensive Demo
```bash
# Run full notification system demonstration
python comprehensive_demo.py
```
This script demonstrates:
- Sample notification creation (system, payment, grade, attendance, report)
- Notification statistics and analytics
- Settings management
- Read/unread status simulation
- Automated notification examples

### Demo Notifications
```bash
# Run basic notification demo
python demo_notifications.py
```
This script creates sample notifications and shows system statistics.

### Testing Results
After running the tests, you should see:
- ✅ All notification tables exist and have correct structure
- ✅ Default notification settings are initialized
- ✅ Notification creation functions work properly
- ✅ Sample notifications are created successfully
- ✅ Statistics show proper categorization and tracking

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For support or questions:
- Check the troubleshooting section
- Review the audit logs for system issues
- Ensure all dependencies are properly installed

---

**Version**: 3.0
**Last Updated**: March 2026
**Python Version**: 3.6+</content>
<parameter name="filePath">c:\Users\d\OneDrive\Desktop\nathan student management\README.md

