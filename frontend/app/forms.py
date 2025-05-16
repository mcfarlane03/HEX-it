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

