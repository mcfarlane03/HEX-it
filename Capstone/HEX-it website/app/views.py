from app import app, csrf
from flask import request, jsonify, send_from_directory
from flask_wtf.csrf import generate_csrf
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta

# Enable CORS for all routes
CORS(app)

# Hardcoded users
HARDCODED_USERS = [
    {"id": 1, "username": "admin", "password": "password123"},
    {"id": 2, "username": "user", "password": "userpass"},
]

# Serve the index page
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# CSRF token endpoint
@csrf.exempt
@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()}), 200

# Generate JWT token
def generate_token(user_id):
    timestamp = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": timestamp,
        "exp": timestamp + timedelta(hours=24)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Login endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        app.logger.debug("Received POST request for /api/auth/login")
        data = request.get_json()
        app.logger.debug(f"Payload received: {data}")

        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        username = data.get('username')
        password = data.get('password')

        # Validate required fields
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        # Check hardcoded users
        user = next((u for u in HARDCODED_USERS if u["username"] == username and u["password"] == password), None)
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401

        # Generate a token
        token = generate_token(user["id"])
        return jsonify({'message': 'Login successful', 'token': token, 'user': user}), 200

    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Registration endpoint (for testing purposes, adds to hardcoded users)
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate required fields
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        # Check if the user already exists
        if any(u["username"] == username for u in HARDCODED_USERS):
            return jsonify({'error': 'User already exists'}), 400

        # Add the new user to the hardcoded list
        new_user = {"id": len(HARDCODED_USERS) + 1, "username": username, "password": password}
        HARDCODED_USERS.append(new_user)

        return jsonify({'message': 'User registered successfully', 'user': new_user}), 201
    except Exception as e:
        app.logger.error(f"Error during registration: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Home view
@app.route('/home', methods=['GET'])
def homeview():
    return "Welcome to the Home Page!", 200