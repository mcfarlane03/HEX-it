from app import app, db, login_manager, csrf
from flask import request, jsonify, send_from_directory, session, redirect, url_for
from flask_wtf.csrf import generate_csrf
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app.forms import LoginForm
from app.models import User
from datetime import datetime, timedelta
from flask_cors import CORS

# Enable CORS for all routes
CORS(app)
import jwt


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
            return jsonify({'error': 'Invalid JSON payload'}), 400

        user_id = data.get('id')
        password = data.get('password')

        # Validate required fields
        if not user_id or not password:
            return jsonify({'error': 'ID and password are required'}), 400

        # Find the user
        user = User.query.get(user_id)
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid ID or password'}), 401

        # Generate a token
        token = generate_token(user_id)
        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        app.logger.error(f"Error during login: {e}")
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