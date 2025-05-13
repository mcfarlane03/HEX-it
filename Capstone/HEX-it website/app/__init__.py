import os
from flask import Flask, request
from .config import Config
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager, current_user
import jwt
from flask import request, g

app = Flask(__name__)

# Minimal CORS config allowing all origins, methods, and headers for testing
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config.from_object(Config)
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads'))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

app.config['SERVER_NAME'] = 'info3180-project-jamdate-9maa.onrender.com'

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

@app.before_request
def log_options_requests():
    if request.method == 'OPTIONS':
        app.logger.debug(f"Received OPTIONS request for {request.path}")

@app.after_request
def set_csrf_cookie(response):
    response.set_cookie('csrf_token', generate_csrf())
    return response

from app import views, models
