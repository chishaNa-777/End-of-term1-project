# Student Management Mobile App

A responsive web-based mobile app for parents to access their children's academic information through the Student Management System.

## Features

- **Dashboard**: Overview of all children with key metrics (GPA, attendance, payment status)
- **Children**: View detailed information about linked children
- **Grades**: Academic progress and GPA tracking
- **Payments**: Fee payment status and history
- **Attendance**: Daily attendance records and statistics
- **Notifications**: Important announcements and updates
- **Messages**: Send messages to administrators and view responses

## Installation & Setup

### Prerequisites
- Python 3.7+
- Flask and dependencies (install via pip)

### Quick Start

1. **Install Dependencies:**
   ```bash
   pip install flask flask-cors pyjwt
   ```

2. **Start the Server:**
   ```bash
   python server.py
   ```

3. **Access the App:**
   - Open your browser and go to: `http://localhost:5000`
   - Or scan the QR code with your mobile device

## Mobile Deployment Options

### Option 1: Progressive Web App (PWA)
The app is already configured as a PWA. On mobile devices:
1. Open the app in Chrome/Safari
2. Tap "Add to Home Screen"
3. The app will install like a native app

### Option 2: Apache Cordova/PhoneGap
To create a native mobile app:

1. **Install Cordova:**
   ```bash
   npm install -g cordova
   ```

2. **Create Cordova Project:**
   ```bash
   cordova create student-app com.studentmanagement.app "Student Management"
   cd student-app
   ```

3. **Add Platform:**
   ```bash
   cordova platform add android
   # or
   cordova platform add ios
   ```

4. **Copy App Files:**
   - Copy `mobile_app.html`, `manifest.json`, `sw.js` to `www/` folder
   - Update `config.xml` with your app details

5. **Build and Run:**
   ```bash
   cordova build android
   cordova run android
   ```

### Option 3: React Native/Flutter
For a more native experience, consider porting to:
- **React Native**: Use the API endpoints with React Native components
- **Flutter**: Create a Dart-based mobile app using the same API

## API Integration

The mobile app connects to the Flask REST API with the following endpoints:

- `POST /api/login` - User authentication
- `GET /api/parent/dashboard` - Parent dashboard data
- `GET /api/parent/grades/{student_id}` - Student grades
- `GET /api/parent/payments/{student_id}` - Payment records
- `GET /api/parent/attendance/{student_id}` - Attendance data
- `GET /api/parent/notifications` - Notifications
- `GET /api/parent/messages` - Messages
- `POST /api/parent/send-message` - Send message to admin

## Security Features

- JWT token-based authentication
- Secure API communication
- Automatic logout on token expiration
- Offline caching with Service Worker

## Browser Support

- Chrome 70+
- Firefox 68+
- Safari 12+
- Edge 79+

## Troubleshooting

### API Connection Issues
- Ensure the Flask server is running on port 5000
- Check that CORS is enabled in the API
- Verify JWT token is valid

### PWA Installation Issues
- Ensure HTTPS in production (required for PWA)
- Check manifest.json is properly configured
- Verify Service Worker is registered

### Mobile Display Issues
- The app is responsive and works on screens 320px and wider
- Test on actual devices for best results

## Development

### File Structure
```
mobile_app.html    # Main app interface
manifest.json       # PWA configuration
sw.js              # Service Worker for offline support
server.py          # Combined server for API and static files
```

### Customization
- Modify CSS in `mobile_app.html` for styling changes
- Update `manifest.json` for app metadata
- Extend JavaScript functions for additional features

## License

This mobile app is part of the Student Management System project.