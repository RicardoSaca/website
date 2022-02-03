from flask_wtf import FlaskForm
from wtforms import TextAreaField,StringField, PasswordField, BooleanField, SubmitField, validators, ValidationError
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from website.models import User

class ContactForm(FlaskForm):
    name = StringField("Name",  [validators.Required("Please enter your name.")])
    email = StringField("Email",  [validators.Email("Not a valid email address."), validators.Required("Please enter your email address.")])
    message = TextAreaField("Message", [validators.Required("Please enter a message.")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me =BooleanField('Rember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username= StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please user a different email address')