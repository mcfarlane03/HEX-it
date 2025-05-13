import os
from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager, current_user
import jwt
from .config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes (minimal configuration for testing)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure secure cookies
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# User loader for Flask-Login
@login_manager.request_loader
def load_user_from_request(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('sub')
            if user_id:
                from app.models import User
                user = db.session.get(User, user_id)
                if user:
                    return user
        except Exception as e:
            app.logger.error(f"Token authentication error: {e}")
    return None

# Log OPTIONS requests for debugging
@app.before_request
def log_options_requests():
    if request.method == 'OPTIONS':
        app.logger.debug(f"Received OPTIONS request for {request.path}")

# Set CSRF token cookie after each request
@app.after_request
def set_csrf_cookie(response):
    response.set_cookie('csrf_token', generate_csrf())
    return response

# Import views and models to register routes and database models
from app import views, models