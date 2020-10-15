# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask.logging import default_handler
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from rich.logging import RichHandler

db = SQLAlchemy()
db_migration = Migrate()
bcrypt = Bcrypt()
csrf_protection = CSRFProtect()
mail = Mail()
login = LoginManager()
login.login_view = "users.login"


def create_app():
    # Create the Flask application
    app = Flask(__name__)

    # Configure the Flask application
    config_type = os.getenv("CONFIG_TYPE", "config.DevelopmentConfig")
    app.config.from_object(config_type)

    register_blueprints(app)
    configure_logging(app)
    register_error_pages(app)
    initialize_extensions(app)

    return app


def register_blueprints(app):
    # Import the blueprints
    from project.stocks import stocks_blueprint
    from project.users import users_blueprint

    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)
    app.register_blueprint(stocks_blueprint)
    app.register_blueprint(users_blueprint, url_prefix="/users")


def configure_logging(app):
    # Logging Configuration
    if app.config["LOG_TO_STDOUT"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    else:
        shell_handler = RichHandler()
        file_handler = RotatingFileHandler(
            "instance/flask-stock-portfolio.log",
            maxBytes=16384,
            backupCount=20,
        )

        shell_formatter = logging.Formatter("%(message)s")
        file_formatter = logging.Formatter(
            (
                "%(asctime)s %(levelname)s: %(message)s "
                "[in %(filename)s:%(lineno)d]"
            ),
        )
        shell_handler.setFormatter(shell_formatter)
        file_handler.setFormatter(file_formatter)

        shell_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

    #   app.logger.addHandler(shell_handler)
    #   app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    app.logger.info("Starting the Flask Stock Portfolio App...")


def register_error_pages(app):
    """
    Error pages registration.

    Error handlers for our 404 and 405 pages.

    """

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_found(e):
        return render_template("405.html"), 405


def initialize_extensions(app):
    """
    Third Part Modules.

    Below are the third party apps being initialized for use with the
    flask app.

    """

    db.init_app(app)
    db_migration.__init__(app, db)
    bcrypt.init_app(app)
    csrf_protection.init_app(app)
    login.init_app(app)
    mail.init_app(app)

    # Flask-Login Configuration
    from project.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
