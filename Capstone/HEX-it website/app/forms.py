# Add any form classes for Flask-WTF here
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Email, Length, Optional, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    username = StringField('Username', validators=[InputRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=80)])

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=80)])
    name = StringField('Name', validators=[InputRequired(), Length(max=80)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=128)])
    photo = FileField('Photo', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

class ProfileForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField('Name', validators=[Optional(), Length(max=255)])
    parish = StringField('Parish', validators=[Optional(), Length(max=80)])
    biography = TextAreaField('Biography', validators=[Optional(), Length(max=500)])
    sex = StringField('Sex', validators=[Optional(), Length(max=20)])
    race = StringField('Race', validators=[Optional(), Length(max=20)])
    birth_year = IntegerField('Birth Year', validators=[Optional(), NumberRange(min=1900, max=2024)])  # Example range
    height = FloatField('Height', validators=[Optional()])
    fav_cuisine = StringField('Favorite Cuisine', validators=[Optional(), Length(max=100)])
    fav_colour = StringField('Favorite Colour', validators=[Optional(), Length(max=50)])
    fav_school_subject = StringField('Favorite School Subject', validators=[Optional(), Length(max=100)])
    political = BooleanField('Political', validators=[Optional()])
    religious = BooleanField('Religious', validators=[Optional()])
    family_oriented = BooleanField('Family Oriented', validators=[Optional()])

class FavouriteForm(FlaskForm):
    fav_user_id_fk = IntegerField('Favorite User ID', validators=[InputRequired()])
    user_id_fk = IntegerField('Your User ID', validators=[InputRequired()])
