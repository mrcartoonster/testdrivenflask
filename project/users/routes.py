# -*- coding: utf-8 -*-
from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from project import db
from project.models import User

from . import users_blueprint
from .forms import LoginForm, RegistrationForm


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
                new_user = User(form.email.data, form.password.data)
                db.session.add(new_user)
                db.session.commit()
                flash(f"Thanks for registering, {new_user.email}!")
                current_app.logger.info(
                    f"Registered new user: ({form.email.data})!",
                )
                return redirect(url_for("stocks.index"))
            except IntegrityError:
                db.session.rollback()
                flash(
                    f"ERROR! Email ({form.email.data}) already exists.",
                    "error",
                )
        else:
            flash("Error in form data!")

    return render_template("users/register.html", form=form)


@users_blueprint.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in, don't allow them to try to log in again
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
                return redirect(url_for("stocks.index"))
        flash("ERROR! Incorrect login credentials.")
    return render_template("users/login.html", form=form)


@users_blueprint.route("/logout")
@login_required
def logout():
    current_app.logger.info(f"Logged out user: {current_user.email}")
    logout_user()
    flash("Goodbye!")
    return redirect(url_for("stocks.index"))
