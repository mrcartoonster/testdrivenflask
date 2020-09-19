# -*- coding: utf-8 -*-
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)

app.secret_key = "BAD_SECRET_KEY"


@app.route("/")
def index():
    app.logger.info("Calling the index function")
    return render_template("index.html")


@app.route("/add_stock", methods=["GET", "POST"])
def add_stock():
    if request.method == "POST":
        # Save the form data to the session object.
        session["stock_symbol"] = request.form["stock_symbol"]
        session["number_of_shares"] = request.form["number_of_shares"]
        session["purchase_price"] = request.form["purchase_price"]

        flash(
            f"Added a new stock ({request.form['stock_symbol']})!",
            "success",
        )

        return redirect((url_for("list_stocks")))

    return render_template("add_stock.html")


@app.route("/stocks")
def list_stocks():
    return render_template("stocks.html")


@app.route("/about")
def about():
    flash("Thank for learning about this site!", "site")
    return render_template("about.html", company_name="TestDriven.io")
