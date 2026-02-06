from flask import Blueprint, render_template, request, redirect, url_for, session
import boto3
import uuid
import os
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError

aws_bp = Blueprint('aws', __name__)

# ---------------- AWS CONFIG ----------------
REGION = 'us-east-1'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:897722679886:aws_topic'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

users_table = dynamodb.Table('Users')
admin_users_table = dynamodb.Table('AdminUsers')
projects_table = dynamodb.Table('Projects')
enrollments_table = dynamodb.Table('Enrollments')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPERS ----------------
def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print("SNS error:", e)

# ---------------- ROUTES ----------------

@aws_bp.route('/')
def aws_index():
    return render_template('aws/index.html')

@aws_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        res = users_table.get_item(Key={'username': username})
        if 'Item' in res:
            return "User already exists"

        users_table.put_item(Item={
            'username': username,
            'password': password
        })

        send_notification("New AWS User", f"{username} signed up")
        return redirect(url_for('aws.login'))

    return render_template('aws/signup.html')

@aws_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        res = users_table.get_item(Key={'username': username})
        if 'Item' in res and res['Item']['password'] == password:
            session['aws_user'] = username
            return redirect(url_for('aws.dashboard'))

        return "Invalid credentials"

    return render_template('aws/login.html')

@aws_bp.route('/dashboard')
def dashboard():
    if 'aws_user' not in session:
        return redirect(url_for('aws.login'))

    username = session['aws_user']
    res = enrollments_table.get_item(Key={'username': username})
    project_ids = res.get('Item', {}).get('project_ids', [])

    projects = []
    for pid in project_ids:
        p = projects_table.get_item(Key={'id': pid})
        if 'Item' in p:
            projects.append(p['Item'])

    return render_template('aws/dashboard.html', projects=projects)

@aws_bp.route('/logout')
def logout():
    session.pop('aws_user', None)
    return redirect(url_for('aws.login'))