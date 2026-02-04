from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import hashlib
import os
import boto3
import uuid

from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# AWS Configuration
REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
# SNS client removed — notifications will use local logging/prints

# DynamoDB Tables (Create these tables in DynamoDB manually)
users_table = dynamodb.Table('Users')
photographers_table = dynamodb.Table('Photographers')
bookings_table = dynamodb.Table('Bookings')
admin_users_table = dynamodb.Table('AdminUsers')
photographer_users_table = dynamodb.Table('PhotographerUsers')

# SNS removed: using local print/logging for notifications

# S3 Configuration
S3_BUCKET = 'your-photography-bucket'
S3_REGION = 'us-east-1'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_notification(subject, message):
    print(f"Notification: {subject} - {message}")

def upload_to_s3(file, folder):
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        key = f"{folder}/{timestamp}_{filename}"
        
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            key,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    try:
        response = users_table.get_item(Key={'username': username})
        return 'Item' in response
    except ClientError as e:
        print(f"Error checking user: {e}")
        return False

def email_exists(email):
    try:
        response = users_table.scan(FilterExpression='email = :email', ExpressionAttributeValues={':email': email})
        return len(response.get('Items', [])) > 0
    except ClientError as e:
        print(f"Error checking email: {e}")
        return False

def authenticate_user(username, password):
    try:
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            user = response['Item']
            if user['password'] == hash_password(password):
                return username
        return None
    except ClientError as e:
        print(f"Error authenticating user: {e}")
        return None

def get_user_by_username(username):
    try:
        response = users_table.get_item(Key={'username': username})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting user: {e}")
        return None

def get_photographer_by_id(photographer_id):
    try:
        response = photographers_table.get_item(Key={'id': photographer_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting photographer: {e}")
        return None

def get_user_bookings(username):
    try:
        response = bookings_table.scan(
            FilterExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        bookings = response.get('Items', [])
        
        for booking in bookings:
            photographer = get_photographer_by_id(booking['photographer_id'])
            booking['photographer_name'] = photographer['name'] if photographer else 'Unknown'
        
        return bookings
    except ClientError as e:
        print(f"Error getting user bookings: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            return render_template('register.html', error='All fields are required')

        if user_exists(username):
            return render_template('register.html', error='Username already exists')

        if email_exists(email):
            return render_template('register.html', error='Email already registered')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')

        try:
            users_table.put_item(Item={
                'username': username,
                'email': email,
                'password': hash_password(password),
                'user_type': 'customer',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            send_notification("New Customer Registration", f"User {username} has registered.")
            return redirect(url_for('login'))
        except ClientError as e:
            print(f"Error registering user: {e}")
            return render_template('register.html', error='Registration failed. Please try again.')

    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login_select.html')

@app.route('/login/customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login_customer.html', error='Username and password required')

        user = authenticate_user(username, password)
        if user is None:
            return render_template('login_customer.html', error='Invalid username or password')

        user_data = get_user_by_username(username)
        if user_data['user_type'] != 'customer':
            return render_template('login_customer.html', error='Please use the appropriate login portal for your account type')

        session['username'] = username
        session['user_type'] = 'customer'
        
        send_notification("Customer Login", f"User {username} has logged in.")
        return redirect(url_for('photographers'))

    return render_template('login_customer.html')

@app.route('/login/photographer', methods=['GET', 'POST'])
def login_photographer():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login_photographer.html', error='Username and password required')

        try:
            response = photographer_users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                return render_template('login_photographer.html', error='Invalid username or password')
            
            photographer_info = response['Item']
            if photographer_info['password'] != hash_password(password):
                return render_template('login_photographer.html', error='Invalid username or password')

            photographer = get_photographer_by_id(photographer_info['photographer_id'])
            session['username'] = username
            session['photographer_id'] = photographer_info['photographer_id']
            session['photographer_name'] = photographer['name'] if photographer else username
            session['user_type'] = 'photographer'
            
            send_notification("Photographer Login", f"Photographer {username} has logged in.")
            return redirect(url_for('photographer_dashboard'))
        except ClientError as e:
            print(f"Error during login: {e}")
            return render_template('login_photographer.html', error='Login failed. Please try again.')

    return render_template('login_photographer.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login_admin.html', error='Username and password required')

        try:
            response = admin_users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                return render_template('login_admin.html', error='Invalid username or password')
            
            admin_info = response['Item']
            if admin_info['password'] != hash_password(password):
                return render_template('login_admin.html', error='Invalid username or password')

            session['username'] = username
            session['user_type'] = 'admin'
            
            send_notification("Admin Login", f"Admin {username} has logged in.")
            return redirect(url_for('admin_dashboard'))
        except ClientError as e:
            print(f"Error during admin login: {e}")
            return render_template('login_admin.html', error='Login failed. Please try again.')

    return render_template('login_admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/photographers')
def photographers():
    if 'username' not in session or session.get('user_type') != 'customer':
        return redirect(url_for('login'))

    try:
        response = photographers_table.scan()
        photographers_list = response.get('Items', [])
        return render_template('photographers.html', photographers=photographers_list)
    except ClientError as e:
        print(f"Error getting photographers: {e}")
        return render_template('photographers.html', photographers=[], error='Failed to load photographers')

@app.route('/book/<photographer_id>', methods=['GET', 'POST'])
def book(photographer_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        photographer = get_photographer_by_id(photographer_id)
        if not photographer:
            return redirect(url_for('photographers'))

        if request.method == 'POST':
            booking_date = request.form.get('booking_date', '').strip()
            booking_time = request.form.get('booking_time', '').strip()
            location = request.form.get('location', '').strip()
            notes = request.form.get('notes', '').strip()

            if not booking_date or not booking_time or not location:
                return render_template('book.html', photographer=photographer, 
                                     photographer_id=photographer_id, 
                                     error='Date, time, and location are required')

            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
            day_name = booking_date_obj.strftime('%A')
            
            if day_name not in photographer.get('availability', []):
                available_days = ', '.join(photographer.get('availability', []))
                return render_template('book.html', photographer=photographer, 
                                     photographer_id=photographer_id, 
                                     error=f'Photographer is not available on {day_name}. Available days: {available_days}')

            booking_id = str(uuid.uuid4())
            bookings_table.put_item(Item={
                'booking_id': booking_id,
                'username': session['username'],
                'photographer_id': photographer_id,
                'date': booking_date,
                'time': booking_time,
                'location': location,
                'notes': notes,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Pending'
            })
            
            send_notification("New Booking", f"Booking {booking_id} created for photographer {photographer['name']}")
            return redirect(url_for('dashboard'))

        return render_template('book.html', photographer=photographer, photographer_id=photographer_id)
    except ClientError as e:
        print(f"Error during booking: {e}")
        return render_template('book.html', photographer={}, photographer_id=photographer_id, error='Booking failed. Please try again.')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        bookings = get_user_bookings(session['username'])
        return render_template('dashboard.html', bookings=bookings)
    except ClientError as e:
        print(f"Error getting dashboard: {e}")
        return render_template('dashboard.html', bookings=[], error='Failed to load dashboard')

@app.route('/photographer-dashboard')
def photographer_dashboard():
    if 'username' not in session or session.get('user_type') != 'photographer':
        return redirect(url_for('login'))

    try:
        response = bookings_table.scan()
        all_bookings = response.get('Items', [])
        return render_template('photographer_dashboard.html', bookings=all_bookings)
    except ClientError as e:
        print(f"Error getting photographer dashboard: {e}")
        return render_template('photographer_dashboard.html', bookings=[], error='Failed to load bookings')

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    try:
        users_response = users_table.scan()
        photographers_response = photographers_table.scan()
        bookings_response = bookings_table.scan()

        users = users_response.get('Items', [])
        photographers = photographers_response.get('Items', [])
        bookings = bookings_response.get('Items', [])

        total_users = len(users)
        customer_users = sum(1 for u in users if u.get('user_type') == 'customer')
        total_photographers = len(photographers)
        total_bookings = len(bookings)

        stats = {
            'total_users': total_users,
            'customer_users': customer_users,
            'total_photographers': total_photographers,
            'total_bookings': total_bookings
        }

        return render_template('admin_dashboard.html', stats=stats)
    except ClientError as e:
        print(f"Error getting admin dashboard: {e}")
        return render_template('admin_dashboard.html', stats={}, error='Failed to load dashboard')

@app.route('/admin/photographers')
def admin_photographers():
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    try:
        response = photographers_table.scan()
        photographers_list = response.get('Items', [])
        return render_template('admin_photographers.html', photographers=photographers_list)
    except ClientError as e:
        print(f"Error getting photographers: {e}")
        return render_template('admin_photographers.html', photographers=[], error='Failed to load photographers')

@app.route('/admin/photographer/add', methods=['GET', 'POST'])
def admin_add_photographer():
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        rate = request.form.get('rate', '').strip()
        contact = request.form.get('contact', '').strip()
        bio = request.form.get('bio', '').strip()
        experience = request.form.get('experience', '').strip()
        location = request.form.get('location', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        skills = request.form.get('skills', '').strip()
        availability = request.form.getlist('availability')
        image_file = request.files.get('image')

        if not all([name, specialization, rate, contact, bio, experience, location, username, password]):
            return render_template('admin_add_photographer.html', error='All fields except image are required')

        try:
            # Check if photographer username already exists
            response = photographer_users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return render_template('admin_add_photographer.html', error='Username already exists')

            rate = int(rate)
            experience = int(experience)
        except ValueError:
            return render_template('admin_add_photographer.html', error='Rate and experience must be numbers')
        except ClientError as e:
            print(f"Error checking username: {e}")
            return render_template('admin_add_photographer.html', error='Failed to add photographer')

        if len(password) < 6:
            return render_template('admin_add_photographer.html', error='Password must be at least 6 characters')

        try:
            photographer_id = str(uuid.uuid4())
            image_url = None

            # Upload image to S3 if provided
            if image_file and image_file.filename:
                image_url = upload_to_s3(image_file, 'photographers')
                if not image_url:
                    return render_template('admin_add_photographer.html', error='Failed to upload image')

            # Add photographer
            photographers_table.put_item(Item={
                'id': photographer_id,
                'name': name,
                'specialization': specialization,
                'rate': rate,
                'contact': contact,
                'bio': bio,
                'image': image_url or 'https://via.placeholder.com/400x400?text=' + name.replace(' ', '+'),
                'experience': experience,
                'location': location,
                'skills': [s.strip() for s in skills.split(',')] if skills else [],
                'availability': availability if availability else ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            })

            # Add photographer user credentials
            photographer_users_table.put_item(Item={
                'username': username,
                'password': hash_password(password),
                'photographer_id': photographer_id,
                'user_type': 'photographer'
            })

            send_notification("New Photographer Added", f"Photographer {name} has been added to the system.")
            return redirect(url_for('admin_photographers'))
        except ClientError as e:
            print(f"Error adding photographer: {e}")
            return render_template('admin_add_photographer.html', error='Failed to add photographer')

    return render_template('admin_add_photographer.html')

@app.route('/admin/photographer/<photographer_id>/delete', methods=['POST'])
def admin_delete_photographer(photographer_id):
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    try:
        photographers_table.delete_item(Key={'id': photographer_id})
        send_notification("Photographer Deleted", f"Photographer {photographer_id} has been removed.")
        return redirect(url_for('admin_photographers'))
    except ClientError as e:
        print(f"Error deleting photographer: {e}")
        return redirect(url_for('admin_photographers'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )