# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from project import create_app, db
from project.models import Stock, User


@pytest.fixture(scope="function")
def new_stock():
    stock = Stock("AAPL", "16", "406.78", 17, datetime(2020, 7, 18))
    return stock


@pytest.fixture(scope="module")
def new_user(test_client_with_app_context):
    user = User("patrick@email.com", "FlaskIsAwesome123")
    return user


@pytest.fixture(scope="module")
def register_default_user(test_client):
    """Registers the default user using the '/users/register' route."""
    test_client.post(
        "/users/register",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
    )


@pytest.fixture(scope="function")
def log_in_default_user(test_client, register_default_user):
    # Log in the user
    test_client.post(
        "/users/login",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
    )

    yield  # this is where the testing happens!

    # Log out the user
    test_client.get("/users/logout", follow_redirects=True)


@pytest.fixture(scope="function")
def confirm_email_default_user(test_client, log_in_default_user):
    # Mark the user as having their email address confirmed
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.email_confirmed = True
    user.email_confirmed_on = datetime.datetime(2020, 7, 8)
    db.session.add(user)
    db.session.commit()

    yield user  # this is where the testing happens!

    # Mark the user as not having their email address confirmed (clean up)
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.email_confirmed = False
    user.email_confirmed_on = None
    db.session.add(user)
    db.session.commit()


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config.from_object("config.TestingConfig")
    flask_app.extensions["mail"].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and db
        with flask_app.app_context():
            flask_app.logger.info(
                "Creating db tables in test_client fixture...",
            )

            # Create the db and the db table(s)
            db.create_all()

        yield testing_client  # this is where the testing happens!

        with flask_app.app_context():
            db.drop_all()


@pytest.fixture(scope="module")
def test_client_with_app_context():
    flask_app = create_app()
    flask_app.config.from_object("config.TestingConfig")
    flask_app.extensions["mail"].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger and db
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="function")
def afterwards_reset_default_user_password():
    yield  # this is where the testing happens!

    # Since a test using this fixture could change the password for the
    # default_user, reset the password back to the default password
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.set_password("FlaskIsAwesome123")
    db.session.add(user)
    db.session.commit()
