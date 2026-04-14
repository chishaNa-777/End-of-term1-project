# Student Management System - Web Application

A modern web-based student management system built with Flask (backend) and React (frontend) for multi-user access and enhanced functionality.

## Features

### Core Features
- **Multi-user Authentication**: JWT-based authentication with role-based access control
- **Student Management**: Complete CRUD operations for student records
- **Academic Tracking**: Subject marks, GPA calculation, and grade management
- **Attendance System**: Daily attendance tracking with statistics
- **Tutorial Management**: Video tutorials and educational content
- **Study Materials**: File upload and management for study notes
- **Analytics Dashboard**: Visual charts and performance analytics
- **Audit Logging**: Comprehensive activity tracking

### Technical Features
- **RESTful API**: Well-structured Flask REST API
- **Modern UI**: Ant Design components with responsive design
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **File Uploads**: Secure file handling for images and documents
- **Real-time Updates**: Dynamic data updates and notifications

## Project Structure

```
web_app/
├── backend/                 # Flask API server
│   ├── app/
│   │   ├── __init__.py     # Flask app factory
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── students.py
│   │   │   └── ...
│   │   └── config.py       # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Server entry point
│   └── .env               # Environment variables
├── frontend/               # React client
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   └── App.js         # Main app component
│   ├── public/
│   └── package.json       # Node dependencies
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd web_app/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy `.env` and update database settings if needed.

5. **Run database migrations:**
   ```bash
   flask db upgrade
   ```

6. **Start the backend server:**
   ```bash
   python run.py
   ```
   Server will run on http://localhost:5000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd web_app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   Frontend will run on http://localhost:3000

## Usage

### Default Credentials
- **Admin User:**
  - Username: `admin`
  - Password: `admin123`

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Register new user (admin only)
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile
- `POST /api/auth/change-password` - Change password

#### Students
- `GET /api/students` - List students (with pagination/search)
- `POST /api/students` - Create student
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student
- `GET /api/students/stats` - Student statistics

#### Subjects & Marks
- `GET /api/subjects` - List subjects/marks
- `POST /api/subjects` - Add marks
- `PUT /api/subjects/{id}` - Update marks
- `DELETE /api/subjects/{id}` - Delete marks

#### Attendance
- `GET /api/attendance` - List attendance records
- `POST /api/attendance` - Mark attendance
- `GET /api/attendance/stats` - Attendance statistics

## Database Schema

### Users Table
- id, username, email, password_hash, role, is_active, created_at, last_login

### Students Table
- id, student_id, name, email, phone, gender, dob, address, program, enrollment_date, status, guardian_name, guardian_phone, image_path, created_at, created_by

### Subjects Table
- id, student_id, subject_name, marks, credits, semester, grade, created_at

### Attendance Table
- id, student_id, date, status, remarks, marked_by, created_at

### Tutorials Table
- id, title, description, video_url, subject, uploaded_by, is_active, created_at

### Study Notes Table
- id, title, subject, file_path, file_name, file_size, uploaded_by, is_active, created_at

### Audit Logs Table
- id, user_id, action, details, ip_address, timestamp

## Development

### Running in Development Mode

1. **Backend:** `python run.py` (with FLASK_ENV=development)
2. **Frontend:** `npm start` (with REACT_APP_API_URL=http://localhost:5000)

### Database Migrations

```bash
cd backend
flask db migrate -m "Migration message"
flask db upgrade
```

### Building for Production

1. **Backend:** Use Gunicorn or similar WSGI server
2. **Frontend:** `npm run build` then serve static files

## Deployment

### Docker Deployment (Recommended)

The application includes a complete Docker setup for easy deployment and scaling.

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

#### Quick Start with Docker

1. **Validate setup (optional):**
   ```bash
   python setup_test.py
   ```

2. **Run the deployment script:**
   ```bash
   # Linux/Mac
   ./deploy.sh

   # Windows
   deploy.bat
   ```

   Or manually:
   ```bash
   cd web_app/docker
   docker-compose up --build
   ```

3. **Verify deployment:**
   ```bash
   python health_check.py
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - API: http://localhost/api
   - Database: localhost:5432 (internal only)

#### Docker Services

- **nginx**: Reverse proxy serving the React frontend and proxying API requests
- **backend**: Flask API server with Gunicorn
- **db**: PostgreSQL database
- **frontend**: React build process (used during build only)

#### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build --force-recreate

# Clean up (removes volumes)
docker-compose down -v
```

#### Production Deployment

1. **Update secrets in docker-compose.yml:**
   ```yaml
   environment:
     - SECRET_KEY=your-production-secret-key
     - JWT_SECRET_KEY=your-production-jwt-secret
     - POSTGRES_PASSWORD=your-strong-password
   ```

2. **Use external database:**
   For production, consider using a managed PostgreSQL service and update the `DATABASE_URL`.

3. **Enable SSL/TLS:**
   Configure nginx with SSL certificates for HTTPS.

### Manual Deployment

#### Backend Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=postgresql://user:password@host:port/db
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

#### Frontend Deployment

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Serve static files:**
   Use nginx, Apache, or any static file server to serve the `build` directory.

### Environment Variables

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Optional: File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
UPLOAD_FOLDER=uploads/

# Optional: CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- File upload restrictions
- Audit logging for all actions
- CORS protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.