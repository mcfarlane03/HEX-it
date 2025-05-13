# Add any model classes for Flask-SQLAlchemy here
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash
from sqlalchemy import Unicode

class User(db.Model):
    # You can use this to change the table name. The default convention is to use
    # the class name. In this case a class name of UserProfile would create a
    # user_profile (singular) table, but if we specify __tablename__ we can change it
    # to `user_profiles` (plural) or some other name.
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(80))
    email = db.Column(db.String(128))
    photo = db.Column(db.String(255), nullable=True)
    date_joined = db.Column(db.DateTime , default=datetime.now)

    # Relationship with Profile
    profile = db.relationship('Profile', backref='user', uselist=False)
    # Relationship with Favourite
    favourites = db.relationship('Favourite', backref='user', foreign_keys='Favourite.user_id_fk')
    favorited_by = db.relationship('Favourite', backref='favorited_user', foreign_keys='Favourite.fav_user_id_fk')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # def get_id(self):
    #     try:
    #         return Unicode(self.id)  # python 2 support
    #     except NameError:
    #         return str(self.id)  # python 3 support

    def get_id(self):
        return str(self.id)  # MUST return a string!

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    def __init__(self, username, password, name, email, photo):
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
        self.name = name
        self.email = email
        self.photo = photo

class Profile(db.Model):
    __tablename__ = 'Profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    parish = db.Column(db.String(80), nullable=True)
    biography = db.Column(db.String(500), nullable=True)
    sex = db.Column(db.String(20), nullable=True)
    race = db.Column(db.String(20), nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)
    fav_cuisine = db.Column(db.String(100), nullable=True)
    fav_colour = db.Column(db.String(50), nullable=True)
    fav_school_subject = db.Column(db.String(100), nullable=True)
    political = db.Column(db.Boolean, nullable=True)
    religious = db.Column(db.Boolean, nullable=True)
    family_oriented = db.Column(db.Boolean, nullable=True)
    
    def __repr__(self):
        return f'<Profile for User ID: {self.user_id_fk}>'
        _

    def __init__(self, user_id_fk, name, parish, biography, sex, race,birth_year, height, fav_cuisine, fav_colour,fav_school_subject, political, religious, family_oriented, photo=None):
        self.user_id_fk = user_id_fk
        self.name = name
        self.parish = parish
        self.biography = biography
        self.sex = sex
        self.race = race
        self.birth_year = birth_year
        self.height = height
        self.fav_cuisine = fav_cuisine
        self.fav_colour = fav_colour
        self.fav_school_subject = fav_school_subject
        self.political = political
        self.religious = religious
        self.family_oriented = family_oriented
        self.photo = photo

        def is_complete(self):
            required_fields = [
                self.name, self.parish, self.biography, self.sex, self.race,
                self.birth_year, self.height, self.fav_cuisine,
                self.fav_colour, self.fav_school_subject,
                self.political, self.religious, self.family_oriented
            ]
            return all(field is not None and field != "" for field in required_fields)

class Favourite(db.Model):
    __tablename__ = 'Favourite'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    fav_user_id_fk = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    
    # Additional relationship to access the favorited user
    # favourite_user = db.relationship('User', foreign_keys=[fav_user_id_fk])
    
    def __repr__(self):
        return f'<Favourite: User {self.user_id_fk} likes User {self.fav_user_id_fk}>'
    
    def __init__(self, user_id_fk, fav_user_id_fk):
        self.user_id_fk = user_id_fk
        self.fav_user_id_fk = fav_user_id_fk