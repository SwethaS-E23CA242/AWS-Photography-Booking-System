from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import hashlib

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change in production

# ============================================================================
# LOCAL DATA STORAGE (In-Memory Dictionaries and Lists)
# These will be replaced with DynamoDB in future milestones
# ============================================================================

# Users storage: {user_id: {username, email, password, created_at}}
users_db = {}

# Photographers storage: {photographer_id: {name, specialization, rate, contact, bio}}
photographers_db = {
    1: {
        'name': 'John Smith',
        'specialization': 'Wedding Photography',
        'rate': 10000,
        'contact': 'john@photographer.com',
        'bio': 'Experienced wedding photographer with passion for capturing emotional moments',
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
        'experience': 12,
        'location': 'Mumbai',
        'skills': ['Wedding Ceremonies', 'Reception Events', 'Prenup Shoots', 'Same-Day Edits'],
        'availability': ['Monday', 'Friday', 'Saturday', 'Sunday']
    },
    2: {
        'name': 'Sarah Johnson',
        'specialization': 'Portrait Photography',
        'rate': 8000,
        'contact': 'sarah@photographer.com',
        'bio': 'Professional portrait photographer specializing in headshots and personal branding',
        'image': 'https://images.unsplash.com/photo-1602233158242-3ba0ac4d2167?q=80&w=736&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'experience': 8,
        'location': 'Bangalore',
        'skills': ['Headshots', 'Personal Branding', 'Studio Portraits', 'Natural Light'],
        'availability': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    },
    3: {
        'name': 'Mike Davis',
        'specialization': 'Event Photography',
        'rate': 15000,
        'contact': 'mike@photographer.com',
        'bio': 'Dynamic event photographer capturing energy and moments at corporate and private events',
        'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop',
        'experience': 10,
        'location': 'Delhi',
        'skills': ['Corporate Events', 'Product Launches', 'Conferences', 'Live Coverage'],
        'availability': ['Thursday', 'Friday', 'Saturday', 'Sunday']
    },
    4: {
        'name': 'Emily Rodriguez',
        'specialization': 'Family Photography',
        'rate': 9000,
        'contact': 'emily@photographer.com',
        'bio': 'Specializing in capturing beautiful family moments and creating lasting memories',
        'image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop',
        'experience': 9,
        'location': 'Pune',
        'skills': ['Family Portraits', 'Maternity', 'Newborn', 'Children Photography'],
        'availability': ['Monday', 'Tuesday', 'Wednesday', 'Saturday', 'Sunday']
    },
    5: {
        'name': 'David Chen',
        'specialization': 'Corporate Photography',
        'rate': 14000,
        'contact': 'david@photographer.com',
        'bio': 'Expert in corporate events, executive headshots, and business photography',
        'image': 'https://images.unsplash.com/photo-1615109398623-88346a601842?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'experience': 11,
        'location': 'Hyderabad',
        'skills': ['Executive Headshots', 'Corporate Events', 'Office Shoots', 'Annual Reports'],
        'availability': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    },
    6: {
        'name': 'Jessica Williams',
        'specialization': 'Fashion Photography',
        'rate': 20000,
        'contact': 'jessica@photographer.com',
        'bio': 'Professional fashion photographer with experience in editorial and commercial work',
        'image': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
        'experience': 13,
        'location': 'Mumbai',
        'skills': ['Fashion Shoots', 'Editorial', 'Lookbooks', 'Product Photography'],
        'availability': ['Wednesday', 'Thursday', 'Friday', 'Saturday']
    },
    7: {
        'name': 'Robert Thompson',
        'specialization': 'Real Estate Photography',
        'rate': 10000,
        'contact': 'robert@photographer.com',
        'bio': 'Specializing in property photography, drone shots, and virtual tours',
        'image': 'https://plus.unsplash.com/premium_photo-1689977927774-401b12d137d6?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'experience': 7,
        'location': 'Gurgaon',
        'skills': ['Property Shoots', 'Aerial Photography', 'Virtual Tours', '3D Visualization'],
        'availability': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    },
    8: {
        'name': 'Amanda Foster',
        'specialization': 'Nature & Landscape Photography',
        'rate': 9000,
        'contact': 'amanda@photographer.com',
        'bio': 'Capturing stunning landscapes and wildlife in their natural habitat',
        'image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=688&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'experience': 6,
        'location': 'Shimla',
        'skills': ['Landscape', 'Wildlife', 'Adventure Photography', 'Travel Photography'],
        'availability': ['Thursday', 'Friday', 'Saturday', 'Sunday']
    },
    9: {
        'name': 'Chris Martinez',
        'specialization': 'Sports Photography',
        'rate': 13000,
        'contact': 'chris@photographer.com',
        'bio': 'Dynamic sports photographer covering all types of athletic events',
        'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop',
        'experience': 9,
        'location': 'Bangalore',
        'skills': ['Sports Events', 'Action Photography', 'Coaching Sessions', 'Tournaments'],
        'availability': ['Saturday', 'Sunday']
    },
    10: {
        'name': 'Lauren Mitchell',
        'specialization': 'Baby & Newborn Photography',
        'rate': 11000,
        'contact': 'lauren@photographer.com',
        'bio': 'Gentle and creative approach to capturing precious baby moments',
        'image': 'https://plus.unsplash.com/premium_photo-1670282393309-70fd7f8eb1ef?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'experience': 8,
        'location': 'Chennai',
        'skills': ['Newborn', 'Baby Portraits', 'Milestone Sessions', 'Maternity'],
        'availability': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']
    }
}

# Bookings storage: {booking_id: {user_id, photographer_id, date, time, location, notes}}
bookings_db = {}

# Helper counter for unique IDs (In production, use database auto-increment)
next_user_id = 1
next_booking_id = 1


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def hash_password(password):
    """
    Hash password using SHA256 for basic security.
    Note: In production, use bcrypt or argon2
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_next_user_id():
    """Get next available user ID (simulating auto-increment)"""
    global next_user_id
    user_id = next_user_id
    next_user_id += 1
    return user_id


def get_next_booking_id():
    """Get next available booking ID (simulating auto-increment)"""
    global next_booking_id
    booking_id = next_booking_id
    next_booking_id += 1
    return booking_id


def user_exists(username):
    """Check if username already exists in the system"""
    return any(user['username'] == username for user in users_db.values())


def email_exists(email):
    """Check if email already exists in the system"""
    return any(user['email'] == email for user in users_db.values())


def authenticate_user(username, password):
    """
    Authenticate user with username and password.
    Returns user_id if authentication successful, None otherwise
    """
    hashed_password = hash_password(password)
    for user_id, user in users_db.items():
        if user['username'] == username and user['password'] == hashed_password:
            return user_id
    return None


def get_user_by_id(user_id):
    """Retrieve user information by user ID"""
    return users_db.get(user_id)


def get_photographer_by_id(photographer_id):
    """Retrieve photographer information by ID"""
    return photographers_db.get(photographer_id)


def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    user_bookings = []
    for booking_id, booking in bookings_db.items():
        if booking['user_id'] == user_id:
            # Enrich booking with photographer information
            photographer = get_photographer_by_id(booking['photographer_id'])
            booking['id'] = booking_id
            booking['photographer_name'] = photographer['name'] if photographer else 'Unknown'
            user_bookings.append(booking)
    return user_bookings


# ============================================================================
# ROUTE: HOME PAGE
# ============================================================================

@app.route('/')
def index():
    """
    Home page route - displays welcome message and navigation options
    """
    return render_template('index.html')


# ============================================================================
# ROUTE: USER REGISTRATION
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route
    GET: Display registration form
    POST: Process registration form submission
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation: Check for empty fields
        if not username or not email or not password or not confirm_password:
            return render_template('register.html', error='All fields are required')

        # Validation: Check if username already exists
        if user_exists(username):
            return render_template('register.html', error='Username already exists')

        # Validation: Check if email already exists
        if email_exists(email):
            return render_template('register.html', error='Email already registered')

        # Validation: Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Validation: Check password length
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')

        # Create new user
        user_id = get_next_user_id()
        users_db[user_id] = {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('register.html')


# ============================================================================
# ROUTE: USER LOGIN
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    GET: Display login form
    POST: Process login form submission
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validation: Check for empty fields
        if not username or not password:
            return render_template('login.html', error='Username and password required')

        # Authenticate user
        user_id = authenticate_user(username, password)

        if user_id is None:
            return render_template('login.html', error='Invalid username or password')

        # Store user information in session
        session['user_id'] = user_id
        session['username'] = username

        # Redirect to photographers page
        return redirect(url_for('photographers'))

    return render_template('login.html')


# ============================================================================
# ROUTE: LOGOUT
# ============================================================================

@app.route('/logout')
def logout():
    """
    User logout route - clears session and redirects to home page
    """
    session.clear()
    return redirect(url_for('index'))


# ============================================================================
# ROUTE: PHOTOGRAPHERS LISTING
# ============================================================================

@app.route('/photographers')
def photographers():
    """
    Display list of all available photographers
    Requires user to be logged in
    """
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Convert photographers_db to a list with IDs included
    photographers_list = []
    for photo_id, photo_info in photographers_db.items():
        photographer = photo_info.copy()
        photographer['id'] = photo_id
        photographers_list.append(photographer)

    return render_template('photographers.html', photographers=photographers_list)


# ============================================================================
# ROUTE: BOOKING FORM
# ============================================================================

@app.route('/book/<int:photographer_id>', methods=['GET', 'POST'])
def book(photographer_id):
    """
    Booking form route for a specific photographer
    GET: Display booking form
    POST: Process booking form submission
    """
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check if photographer exists
    photographer = get_photographer_by_id(photographer_id)
    if not photographer:
        return redirect(url_for('photographers'))

    if request.method == 'POST':
        booking_date = request.form.get('booking_date', '').strip()
        booking_time = request.form.get('booking_time', '').strip()
        location = request.form.get('location', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validation: Check for required fields
        if not booking_date or not booking_time or not location:
            return render_template('book.html', photographer=photographer, 
                                 photographer_id=photographer_id, 
                                 error='Date, time, and location are required')

        # Validation: Check if booking date is on an available day
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
        day_name = booking_date_obj.strftime('%A')  # Get day name (e.g., 'Monday')
        
        if day_name not in photographer.get('availability', []):
            available_days = ', '.join(photographer.get('availability', []))
            return render_template('book.html', photographer=photographer, 
                                 photographer_id=photographer_id, 
                                 error=f'Photographer is not available on {day_name}. Available days: {available_days}')

        # Create new booking
        booking_id = get_next_booking_id()
        bookings_db[booking_id] = {
            'user_id': session['user_id'],
            'photographer_id': photographer_id,
            'date': booking_date,
            'time': booking_time,
            'location': location,
            'notes': notes,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Pending'
        }

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    return render_template('book.html', photographer=photographer, photographer_id=photographer_id)


# ============================================================================
# ROUTE: USER DASHBOARD
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """
    User dashboard displaying all bookings made by the logged-in user
    """
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    bookings = get_user_bookings(user_id)

    return render_template('dashboard.html', bookings=bookings)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 - Page Not Found errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 - Server errors"""
    return render_template('500.html'), 500


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Run Flask development server
    # Set debug=True for development, change to False in production
    app.run(
        host='localhost',
        port=5000,
        debug=True
    )
