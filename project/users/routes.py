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
from sqlalchemy.exc import IntegrityError

from project import db
from project.models import User

from . import users_blueprint
from .forms import RegistrationForm


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
                    f"Registered new user: ({form.email.data})",
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

    else:
        return render_template("users/register.html", form=form)
