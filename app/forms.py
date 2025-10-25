from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import Email,Length,DataRequired

class RegistrastionFrom(FlaskForm):
    name = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators={DataRequired(),Length(10)})
    submit = SubmitField("Sing Up")

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired(),Length(10)])
    submit = SubmitField("Sing In")