"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from app import app, db, login_manager
from flask import flash, render_template, request, jsonify, send_file, send_from_directory, session
import os, jwt, base64
from werkzeug.utils import secure_filename
from flask_wtf.csrf import generate_csrf
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app.forms import FavouriteForm, LoginForm, SignUpForm, ProfileForm
from app.models import User, Favourite, Profile
from datetime import datetime, timedelta

###
# Routing for your application.
###

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
@login_required
def delete_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id_fk != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        db.session.delete(profile)
        db.session.commit()
        return jsonify({'message': 'Profile deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    data = request.form
    try:
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        # Add other fields as needed
        photo_file = request.files.get('photo')
        if photo_file:
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)
            user.photo = filename
        db.session.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
    if user.photo:
        user_dict['photo'] = f"/api/photo/{user.photo}"
    else:
        user_dict['photo'] = None
    return jsonify(user_dict)

from flask import send_from_directory

from flask import send_from_directory

from flask import send_from_directory, abort

from mimetypes import guess_type

import logging

@app.route('/api/photo/<filename>', methods=['GET'])
def get_photo(filename):
    # Allow public access to photos without login required
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    abs_upload_folder = os.path.abspath(upload_folder)
    file_path = os.path.join(abs_upload_folder, filename)
    app.logger.debug(f"Serving photo from path: {file_path}")
    if not os.path.isfile(file_path):
        app.logger.error(f"File not found: {file_path}")
        abort(404)
    try:
        mime_type, _ = guess_type(file_path)
        response = send_from_directory(abs_upload_folder, filename, mimetype=mime_type)
        # Remove any authentication or authorization headers that might block access
        response.headers.pop('WWW-Authenticate', None)
        response.headers.pop('Authorization', None)
        return response
    except PermissionError:
        abort(403)



from app import csrf

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

@app.route('/api/register', methods=["POST"])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            username = request.form['username']
            password = request.form['password']
            name = request.form['name']
            email = request.form['email']
            photo = request.files['photo']

            filename = secure_filename(f"{username}_profile_photo.jpg")
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            # with open(photo_path, "wb") as fh:
            #     fh.write(base64.decodebytes(photo.split(",")[1].encode()))

            user = User(username, password, name, email, filename)
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': f"Account successfully created for {username}!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({"errors": form_errors(form)}), 400

@app.route('/debug/users', methods=['GET'])
def debug_users():
    if app.debug:  # Only works in debug mode
        users = User.query.all()
        user_list = [{"id": user.id, "username": user.username} for user in users]
        return jsonify(user_list)
    return jsonify({"error": "Not available"}), 403



from app import csrf
import traceback

@csrf.exempt
@app.route('/api/auth/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    try:
        app.logger.debug(f"Login form data: {request.form}")
        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                token = generate_token(user.id)
                login_user(user)
                session['login_time'] = datetime.utcnow().isoformat()
                app.logger.debug(f"User logged in: id={user.id}, username={user.username}")
                return jsonify({'message': 'Login successful!', 'token': token, 'user': {'id': user.id, 'username': user.username, 'name': user.name, 'email': user.email}}), 200
            return jsonify({'errors': ['Invalid credentials']}), 401
        app.logger.debug(f"Login form errors: {form.errors}")
        return jsonify({'errors': form_errors(form)}), 400
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'errors': ['An unexpected error occurred.']}), 500

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(User).filter_by(id=id)).scalar()

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out', 'redirect_url': "/"}), 200

@app.route('/api/profiles', methods=['GET'])
@login_required
def list_profiles():
    app.logger.debug(f"Current user id: {current_user.id}")
    all_profiles = Profile.query.order_by(Profile.id.desc()).all()
    app.logger.debug(f"All profiles in DB: {[p.user_id_fk for p in all_profiles]}")
    profiles = Profile.query.filter(Profile.user_id_fk != current_user.id).order_by(Profile.id.desc()).limit(4).all()
    app.logger.debug(f"Filtered profiles found: {profiles}")
    profiles_list = []
    for p in profiles:
        profile_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        photo = getattr(p, 'photo', None)
        if photo and photo.lower() != 'null':
            profile_dict['photo'] = f"/api/photo/{photo}"
        else:
            profile_dict['photo'] = None
        app.logger.debug(f"Profile data: {profile_dict}")
        profiles_list.append(profile_dict)
    return jsonify(profiles_list)

from app import csrf

@csrf.exempt
@app.route('/api/debug/add_test_profiles', methods=['POST'])
def add_test_profiles():
    try:
        # Add test profiles for current user and others
        from app.models import Profile, User
        from app import db
        from werkzeug.security import generate_password_hash

        # Create test users if not exist
        user1 = User.query.filter_by(username='testuser1').first()
        if not user1:
            user1 = User(username='testuser1', password=generate_password_hash('password1'), name='Test User 1', email='test1@example.com', photo=None)
            db.session.add(user1)
            db.session.commit()

        user2 = User.query.filter_by(username='testuser2').first()
        if not user2:
            user2 = User(username='testuser2', password=generate_password_hash('password2'), name='Test User 2', email='test2@example.com', photo=None)
            db.session.add(user2)
            db.session.commit()

        # Add profiles for user1 and user2
        profile1 = Profile(user_id_fk=user1.id, name='Test Profile 1', parish='Parish1', biography='Bio1', sex='male', race='race1', birth_year=1990, height=70.0, fav_cuisine='Cuisine1', fav_colour='Red', fav_school_subject='Math', political=True, religious=False, family_oriented=True, photo=None)
        profile2 = Profile(user_id_fk=user2.id, name='Test Profile 2', parish='Parish2', biography='Bio2', sex='female', race='race2', birth_year=1992, height=65.0, fav_cuisine='Cuisine2', fav_colour='Blue', fav_school_subject='Science', political=False, religious=True, family_oriented=False, photo=None)

        db.session.add(profile1)
        db.session.add(profile2)
        db.session.commit()

        return jsonify({'message': 'Test profiles added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
@login_required
def get_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    # Convert SQLAlchemy model to dict excluding internal state
    profile_dict = {c.name: getattr(profile, c.name) for c in profile.__table__.columns}
    return jsonify(profile_dict)

@app.route('/api/profiles/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_profiles(user_id):
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    profiles = Profile.query.filter_by(user_id_fk=user_id).all()
    profiles_list = []
    for p in profiles:
        profile_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        photo = getattr(p, 'photo', None)
        if photo:
            profile_dict['photo'] = f"/api/photo/{photo}"
        else:
            profile_dict['photo'] = None
        profiles_list.append(profile_dict)
    return jsonify(profiles_list)

from app import csrf

@csrf.exempt
@app.route('/api/profiles/<int:user_id>/favourite', methods=['POST', 'DELETE'])
# @login_required  # Temporarily disabled for debugging 403 error
def favourite_profile(user_id):
    app.logger.debug(f"favourite_profile called with user_id={user_id}, current_user={current_user}")
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot favourite yourself'}), 403

    existing = Favourite.query.filter_by(user_id_fk=current_user.id, fav_user_id_fk=user_id).first()

    if request.method == 'POST':
        if existing:
            return jsonify({'message': 'Already favourited'}), 200
        fav = Favourite(user_id_fk=current_user.id, fav_user_id_fk=user_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'message': 'User favourited'}), 201

    elif request.method == 'DELETE':
        if not existing:
            return jsonify({'message': 'Not favourited'}), 200
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'message': 'User unfavourited'}), 200



from app import csrf

@csrf.exempt
@app.route('/api/profiles', methods=['POST'])
@login_required
def create_profile():
    print("create_profile route called")  # Debug print
    print("Request form data:", request.form)  # Debug print
    print("Request files:", request.files)  # Debug print
    form = ProfileForm(formdata=request.form)
    form.csrf_enabled = False  # Disable CSRF for API
    print("Form data received:", form.data)  # Debug print
    if form.validate():
        print("Form validated successfully")  # Debug print
        try:
            photo_file = request.files.get('photo')
            filename = None
            if photo_file:
                filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo_file.save(photo_path)

            profile = Profile(
                user_id_fk=current_user.id,
                name=form.name.data if form.name.data else '',
                parish=form.parish.data,
                biography=form.biography.data,
                sex=form.sex.data,
                race=form.race.data,
                birth_year=form.birth_year.data,
                height=form.height.data,
                fav_cuisine=form.fav_cuisine.data,
                fav_colour=form.fav_colour.data,
                fav_school_subject=form.fav_school_subject.data,
                political=form.political.data,
                religious=form.religious.data,
                family_oriented=form.family_oriented.data,
                photo=filename
            )
            db.session.add(profile)
            db.session.commit()
            return jsonify({'message': 'Profile created successfully!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        print("Form validation failed")  # Debug print
        print("ProfileForm errors:", form.errors)  # Explicit print for debugging
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Validation error in {field}: {error}")
        # Return JSON error response instead of HTML error page
        response = jsonify({'errors': form_errors(form)})
        response.status_code = 400
        return response

@csrf.exempt
@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
@login_required
def update_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id_fk != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    form = ProfileForm(formdata=request.form)
    form.csrf_enabled = False
    if form.validate():
        try:
            photo_file = request.files.get('photo')
            if photo_file:
                filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo_file.save(photo_path)
                profile.photo = filename
            profile.name = form.name.data if form.name.data else profile.name
            profile.parish = form.parish.data
            profile.biography = form.biography.data
            profile.sex = form.sex.data
            profile.race = form.race.data
            profile.birth_year = form.birth_year.data
            profile.height = form.height.data
            profile.fav_cuisine = form.fav_cuisine.data
            profile.fav_colour = form.fav_colour.data
            profile.fav_school_subject = form.fav_school_subject.data
            profile.political = form.political.data
            profile.religious = form.religious.data
            profile.family_oriented = form.family_oriented.data
            db.session.commit()
            return jsonify({'message': 'Profile updated successfully!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'errors': form_errors(form)}), 400

@app.route('/api/users/<int:user_id>/favourites', methods=['GET'])
@login_required
def user_favourites(user_id):
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    try:
        favourites = Favourite.query.filter_by(user_id_fk=user_id).all()
        result = []
        for f in favourites:
            user = User.query.get(f.fav_user_id_fk)
            if user:
                user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
                if user.photo:
                    user_dict['photo'] = f"/api/photo/{user.photo}"
                else:
                    user_dict['photo'] = None
                result.append(user_dict)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/favourites/top/<int:N>', methods=['GET'])
@login_required
def top_favorited_users(N):
    results = db.session.query(Favourite.fav_user_id_fk, db.func.count(Favourite.id).label('fav_count')).group_by(Favourite.fav_user_id_fk).order_by(db.desc('fav_count')).limit(N).all()

    users = [User.query.get(uid).__dict__ for uid, count in results]
    return jsonify(users)


###
# The functions below should be applicable to all Flask apps.
###


# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    # response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    # response.headers["Content-Type"] = "application/json"
    return response


from flask import jsonify

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error handler returning JSON."""
    return jsonify({'error': 'Resource not found'}), 404




@app.route('/api/profiles/matches/<int:profile_id>', methods=['GET'])
@login_required
def get_matches(profile_id):
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401
    
    try:
        token = token.split(" ")[1]  # Extract the actual token from "Bearer <token>"
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        if decoded_token.get('sub') != current_user.id:

            return jsonify({"error": "Unauthorized access"}), 403

        current_profile = Profile.query.get_or_404(profile_id)  # Get the selected profile
        other_profiles = Profile.query.filter(Profile.user_id_fk != current_profile.user_id_fk).all()  # Exclude current user

        matched_profiles = []

        for profile in other_profiles:
            # Add these defensive checks here before any calculations
            if current_profile.birth_year is None or profile.birth_year is None:
                continue
            if current_profile.height is None or profile.height is None:
                continue
            if current_profile.fav_cuisine is None or profile.fav_cuisine is None:
                continue
            if current_profile.fav_colour is None or profile.fav_colour is None:
                continue
            if current_profile.fav_school_subject is None or profile.fav_school_subject is None:
                continue

            # Then the existing age and height difference checks follow
            if abs(current_profile.birth_year - profile.birth_year) > 5:
                continue

            if current_profile.user_id_fk == profile.user_id_fk:
                continue

            if not (3 <= abs(current_profile.height - profile.height) <= 10):
                continue

            # Count shared preferences
            shared_traits = sum([
                current_profile.fav_cuisine.lower() == profile.fav_cuisine.lower(),
                current_profile.fav_colour.lower() == profile.fav_colour.lower(),
                current_profile.fav_school_subject.lower() == profile.fav_school_subject.lower(),
                current_profile.political == profile.political,
                current_profile.religious == profile.religious,
                current_profile.family_oriented == profile.family_oriented
            ])

            # Minimum 3 shared traits required
            if shared_traits >= 3:
                matched_profiles.append({
                    "profile_id": profile.id,
                    "user_id": profile.user_id_fk,
                    "name": User.query.get(profile.user_id_fk).name,
                    "photo": f"/api/photo/{profile.photo}",
                    "birth_year": profile.birth_year,
                    "height": profile.height,
                    "fav_cuisine": profile.fav_cuisine,
                    "fav_colour": profile.fav_colour,
                    "fav_school_subject": profile.fav_school_subject,
                    "political": profile.political,
                    "religious": profile.religious,
                    "family_oriented": profile.family_oriented
                })

        return jsonify({"matching_profiles": matched_profiles}), 200
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


