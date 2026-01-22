# Photography Booking Platform - Milestone 1

A beginner-friendly Flask web application for booking professional photographers. This is the first milestone focusing on web application development and setup using local data storage.

## 📋 Project Overview

This platform allows users to:
- Register and create accounts
- Login to their accounts
- Browse a list of professional photographers with different specializations
- Book photographers for specific events or sessions
- View and manage their bookings on a personal dashboard

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3
- **Data Storage**: Local dictionaries and lists (in-memory)
- **IDE**: Visual Studio Code

## 📁 Project Structure

```
Photography/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── templates/                      # HTML templates
│   ├── index.html                 # Home page
│   ├── register.html              # User registration
│   ├── login.html                 # User login
│   ├── photographers.html         # Browse photographers
│   ├── book.html                  # Booking form
│   └── dashboard.html             # User dashboard
└── static/                        # Static files
    └── style.css                  # Stylesheet
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Visual Studio Code (recommended)

### Installation

1. **Clone or create the project directory**
   ```bash
   cd Photography
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to**
   ```
   http://localhost:5000
   ```

3. **Create an account and start booking!**

## 📚 Features Implemented (Milestone 1)

### ✅ Authentication System
- User registration with validation
- User login authentication
- Session management
- Password hashing (SHA256)
- Logout functionality

### ✅ Photographer Management
- List of pre-loaded photographers
- Photographer profiles with specializations
- Contact information
- Hourly rates

### ✅ Booking System
- Create new bookings
- Select date, time, and location
- Add optional notes
- Store bookings locally

### ✅ User Dashboard
- View all user bookings
- Booking status tracking
- Booking details display
- Summary statistics

### ✅ Web Interface
- Responsive design (works on mobile and desktop)
- Professional styling with gradient effects
- Navigation bar with contextual links
- Error handling and validation messages
- Alert messages for user feedback

### ✅ Code Quality
- Well-commented code
- Clean separation of concerns
- Utility functions for common operations
- Beginner-friendly implementation

## 🔐 Security Notes

### Current Implementation (Milestone 1)
- Password hashing using SHA256
- Session-based authentication
- Basic input validation

### Important for Production
⚠️ **DO NOT use this in production!** This implementation is for educational purposes only.

For production deployments, implement:
- Bcrypt or Argon2 for password hashing
- HTTPS/SSL encryption
- CSRF protection
- SQL injection prevention
- Rate limiting on login attempts
- Secure session management

## 💾 Data Storage (Milestone 1)

All data is stored in local dictionaries and lists in memory:

```python
users_db = {}           # Stores user information
photographers_db = {}   # Stores photographer profiles
bookings_db = {}        # Stores booking records
```

**Important Notes:**
- Data is reset when the application restarts
- Not suitable for production use
- Designed for easy migration to DynamoDB in future milestones

## 🔄 Future Milestones

### Milestone 2: Cloud Integration
- Replace local dictionaries with AWS DynamoDB
- Implement user authentication with AWS Cognito
- Add image storage with S3
- Deploy on AWS Lambda with API Gateway

### Milestone 3: Advanced Features
- Payment processing
- Email notifications
- Rating and reviews
- Calendar integration

### Milestone 4: Production Deployment
- CI/CD pipeline with GitHub Actions
- CloudFormation for infrastructure as code
- Monitoring and logging
- Performance optimization

## 📖 Code Structure

### app.py Organization

1. **Imports and Initialization** - Flask setup and configuration
2. **Data Storage** - Local dictionary definitions
3. **Utility Functions** - Helper functions for common operations
4. **Routes** - Flask route handlers
5. **Error Handlers** - 404 and 500 error handling
6. **Application Entry Point** - Server startup code

### Utility Functions

- `hash_password()` - Encrypt passwords
- `get_next_user_id()` - Generate unique user IDs
- `get_next_booking_id()` - Generate unique booking IDs
- `user_exists()` - Check duplicate usernames
- `email_exists()` - Check duplicate emails
- `authenticate_user()` - Verify login credentials
- `get_user_by_id()` - Retrieve user information
- `get_photographer_by_id()` - Retrieve photographer data
- `get_user_bookings()` - Get user's bookings

## 🔗 Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/photographers` | GET | Browse photographers |
| `/book/<id>` | GET, POST | Book a photographer |
| `/dashboard` | GET | View user bookings |

## 🧪 Testing the Application

### Demo Workflow

1. **Register a new account**
   - Click "Register" on the home page
   - Fill in username, email, and password
   - Submit the form

2. **Login**
   - Click "Login" on the home page
   - Enter your credentials
   - Click "Login"

3. **Browse photographers**
   - You'll be redirected to the photographers page
   - View all available photographers and their specializations

4. **Make a booking**
   - Click "Book This Photographer" on any photographer card
   - Fill in the booking date, time, and location
   - Optionally add notes about your event
   - Click "Confirm Booking"

5. **View your bookings**
   - Click "My Bookings" in the navigation bar
   - See all your bookings in a table format
   - View booking details and status

## 🎨 Styling

The application uses a modern, professional design with:
- **Color Scheme**: Blue (#2563eb), Green (#10b981), Red (#ef4444)
- **Typography**: Segoe UI with semantic hierarchy
- **Responsive Grid**: CSS Grid and Flexbox layouts
- **Hover Effects**: Smooth transitions and transforms
- **Mobile Friendly**: Adapts to screens from 480px to 1200px+

## 📝 Code Comments

All code includes detailed comments explaining:
- Purpose of each section
- Function parameters and return values
- Important business logic
- Data structure organization
- Future migration considerations

## ❓ FAQ

**Q: Can I use this in production?**
A: No, this is for learning purposes only. Implement proper security for production.

**Q: How do I backup my bookings?**
A: Since data is stored in memory, restart the server to reset. For persistence, upgrade to Milestone 2 with DynamoDB.

**Q: Can I customize the photographers list?**
A: Yes, edit the `photographers_db` dictionary in `app.py` to add/remove photographers.

**Q: How do I change the secret key?**
A: Change the value of `app.secret_key` in app.py. Use a strong random value for production.

## 📞 Support

For issues or questions:
1. Check the code comments in app.py
2. Review the HTML templates for frontend structure
3. Consult the Future Requirement notes for upcoming features

## 📄 License

This project is part of a guided cloud computing course. Use for educational purposes only.

## 👨‍💻 Author

Photography Platform Development Team
Date: January 2026

---

**Happy Booking! 📸**
