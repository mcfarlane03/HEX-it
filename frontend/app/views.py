import os
import sys

# Manually add the path to loraRecv/src for importing matlab_intt
# This is necessary because the script is not in the same directory as the app
lora_recv_src_path = r"C:\Users\donta\OneDrive\Desktop\HEX-it_website\HEX-it\loraRecv\src"

if lora_recv_src_path not in sys.path:
    sys.path.insert(0, lora_recv_src_path)

from matlab_int import start_matlab_script_async, stop_matlab_script

from app import app, db, login_manager, csrf
from flask import request, jsonify, send_from_directory, session, redirect, url_for
from flask_wtf.csrf import generate_csrf
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app.forms import LoginForm
from app.models import User
from datetime import datetime, timedelta
from flask_cors import CORS
import threading
import jwt
import logging

# Enable CORS for all routes
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@csrf.exempt
@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()}), 200

def generate_token(user_id):
    timestamp = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": timestamp,
        "exp": timestamp + timedelta(hours=24)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@csrf.exempt
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        app.logger.debug("Received POST request for /api/auth/login")
        data = request.get_json()
        app.logger.debug(f"Payload received: {data}")

        if not data:
            app.logger.error("No JSON payload received")
            return jsonify({'error': 'Invalid JSON payload'}), 400

        user_id = data.get('id')
        password = data.get('password')

        # Validate required fields
        if not user_id or not password:
            app.logger.error("ID or password missing in payload")
            return jsonify({'error': 'ID and password are required'}), 400

        # Find the user
        user = User.query.get(user_id)
        if not user:
            app.logger.error(f"User not found: {user_id}")
            return jsonify({'error': 'Invalid ID or password'}), 401

        if not user.check_password(password):
            app.logger.error(f"Password check failed for user: {user_id}")
            return jsonify({'error': 'Invalid ID or password'}), 401

        # Generate a token
        token = generate_token(user_id)

        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        app.logger.error(f"Error during login: {e}\\n{tb}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/home', methods=['GET'])
def homeview():
    return "Welcome to the Home Page!", 200

@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(User).filter_by(id=id)).scalar()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user_id = data.get('id')
        password = data.get('password')

        # Validate required fields
        if not user_id or not password:
            return jsonify({'error': 'ID and password are required'}), 400

        # Check if the user already exists
        if User.query.get(user_id):
            return jsonify({'error': 'User already exists'}), 400

        # Create a new user
        user = User(id=user_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        app.logger.error(f"Error during registration: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@csrf.exempt
@app.route('/api/matlab/start', methods=['POST'])
def start_matlab():
    try:
        # Start MATLAB asynchronously on button press
        success, message = start_matlab_script_async()
        if success:
            return jsonify({'message': message}), 200
        else:
            app.logger.error(f"MATLAB async start failed: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        app.logger.error(f"Exception in /api/matlab/start: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@csrf.exempt
@app.route('/api/matlab/stop', methods=['POST'])
def stop_matlab():
    try:
        success, message = stop_matlab_script()
        if success:
            return jsonify({'message': message}), 200
        else:
            app.logger.error(f"MATLAB stop failed: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        app.logger.error(f"Exception in /api/matlab/stop: {e}")
        return jsonify({'error': 'Internal server error'}), 500
