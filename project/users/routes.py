# -*- coding: utf-8 -*-
from flask import abort, flash, render_template

from . import users_blueprint


@users_blueprint.route("/about")
def about():
    flash("Thanks for learning about this site!", "info")
    return render_template("users/about.html", company_name="TestDriven.io")


# 403 error example
@users_blueprint.route("/admin")
def admin():
    abort(403)
