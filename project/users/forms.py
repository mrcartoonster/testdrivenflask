# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email: ",
        validators=[DataRequired(), Email(), Length(min=6, max=120)],
    )
    password = PasswordField(
        "Password: ",
        validators=[DataRequired(), Length(min=6, max=40)],
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(
        "Email: ",
        validators=[DataRequired(), Email(), Length(min=6, max=100)],
    )
    password = PasswordField(
        "Password: ",
        validators=[DataRequired()],
    )
    remember_me = BooleanField("Remember me: ")
    submit = SubmitField("Login")


class EmailForm(FlaskForm):
    email = StringField(
        "Email:",
        validators=[DataRequired(), Email(), Length(min=6, max=100)],
    )
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    password = PasswordField("New Password: ", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    """
    Form that will allow password change.

    View that will handle this form is
    project.users.route.change_password().

    """

    current_password = PasswordField(
        "Current Password: ",
        validators=[DataRequired()],
    )
    new_password = PasswordField("New Password: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
