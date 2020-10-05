# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
from urllib.parse import urlparse

from flask import (
    abort,
    copy_current_request_context,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature
from sqlalchemy.exc import IntegrityError

from project import db, mail
from project.models import User

from . import users_blueprint
from .forms import LoginForm, RegistrationForm


def generate_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
    )

    confirm_url = url_for(
        "users.confirm_email",
        token=confirm_serializer.dumps(
            user_email,
            salt="email-confirmation-salt",
        ),
        _external=True,
    )

    return Message(
        subject="Flask Stock Portfolio App - Confirm Your Email Address",
        html=render_template(
            "users/email_confirmation.html",
            confirm_url=confirm_url,
        ),
        recipients=[user_email],
    )


@users_blueprint.route("/login", methods=["GET", "POST"])
def login():
    # If the user is already logged in, don't allow them to try to log in again
    if current_user.is_authenticated:
        flash("Already logged in!")
        current_app.logger.info(
            f"Duplicate login attempt by user: {current_user.email}",
        )
        return redirect(url_for("stocks.index"))

    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.is_password_correct(form.password.data):
                # User's credentials have been validated, so log them in
                login_user(user, remember=form.remember_me.data)
                flash(f"Thanks for logging in, {current_user.email}!")
                current_app.logger.info(
                    f"Logged in user: {current_user.email}",
                )
                if not request.args.get("next"):
                    return redirect(url_for("users.user_profile"))

                next_url = request.args.get("next")
                if (
                    urlparse(next_url).scheme != ""
                    or urlparse(next_url).netloc != ""
                ):
                    current_app.logger.info(
                        f"Invalid next path in login request: {next_url}",
                    )
                    logout_user()
                    return abort(400)

                current_app.logger.info(
                    f"Redirecting after valid login to: {next_url}",
                )
                return redirect(next_url)

        flash("ERROR! Incorrect login credentials.")
    return render_template("users/login.html", form=form)


@users_blueprint.route("/logout")
@login_required
def logout():
    current_app.logger.info(f"Logged out user: {current_user.email}")
    logout_user()
    flash("Goodbye!")
    return redirect(url_for("stocks.index"))


@users_blueprint.route("/about")
def about():
    flash("Thanks for learning about this site!", "info")
    return render_template("users/about.html", company_name="TestDriven.io")


# 403 error example
@users_blueprint.route("/admin")
def admin():
    abort(403)


@users_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                new_user = User(
                    form.email.data,
                    form.password.data,
                    datetime.now(),
                )
                db.session.add(new_user)
                db.session.commit()
                flash(
                    (
                        f"Thanks for registering, {new_user.email}!"
                        " Please check your email to confirm email address."
                    ),
                )
                current_app.logger.info(
                    f"Registered new user: ({form.email.data})!",
                )

                @copy_current_request_context
                def send_email(message):
                    with current_app.app_context():
                        mail.send(message)

                msg = generate_confirmation_email(form.email.data)
                email_thread = Thread(target=send_email, args=[msg])
                email_thread.start()

                return redirect(url_for("users.login"))
            except IntegrityError:
                db.session.rollback()
                flash(
                    f"ERROR! Email ({form.email.data}) already exists.",
                    "error",
                )
        else:
            flash("Error in form data!")

    return render_template("users/register.html", form=form)


@users_blueprint.route("/profile")
@login_required
def user_profile():
    return render_template("users/profile.html")


@users_blueprint.route("/confirm/<token>")
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(
            current_app.config["SECRET_KEY"],
        )
        email = confirm_serializer.loads(
            token,
            salt="email-confirmation-salt",
            max_age=3600,
        )
    except BadSignature:
        flash("The confirmation link is invalid or has expired.", "error")
        current_app.logger.info(
            "Invaid or exired confirmation link received "
            f"from IP address: {request.remote_addr}",
        )
        return redirect(url_for("users.login"))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash("Account already confirmed. Please login", "info")
        current_app.logger.info(
            f"Confirmation link received for a confirmed user: {user.email}",
        )
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("Thank you for confirming your email address!", "success")
        current_app.logger.info(f"Email address confirmed for: {user.email}")

    return redirect(url_for("stocks.index"))
