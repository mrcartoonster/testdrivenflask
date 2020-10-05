# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from project import create_app, db
from project.models import Stock, User


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config.from_object("config.TestingConfig")
    flask_app.extensions["mail"].suppress = True

    # Create a test client using the Flask application configured for testing.
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger.
        with flask_app.app_context():
            flask_app.logger.info(
                "Creating database tables in test_client fixture",
            )

            # Create the database and the database tables.
            db.create_all()

        yield testing_client  # Where the tests are going one.

        with flask_app.app_context():
            db.drop_all()


@pytest.fixture(scope="module")
def new_stock():
    """Base Stocks to add."""
    stock = Stock("AAPL", "16", "406.78")
    return stock


@pytest.fixture(scope="module")
def new_user():
    user = User("patrick@email.com", "FlaskIsAwesome123")
    return user


@pytest.fixture(scope="module")
def register_default_user(test_client):
    user = User("patrick@gmail.com", "FlaskIsAwesome123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def log_in_default_user(test_client, register_default_user):
    # Log in the user
    test_client.post(
        "/users/login",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
        follow_redirects=True,
    )

    yield register_default_user  # this is where the testing happens!

    # Log out the user
    test_client.get("/users/logout", follow_redirects=True)


@pytest.fixture(scope="function")
def confirm_email_default_user(test_client, log_in_default_user):
    # Mark the user as having their email address confirmed
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.email_confirmed = True
    user.email_confirmed_on = datetime(2020, 7, 8)
    db.session.add(user)
    db.session.commit()

    yield user  # This is where the testing happens!

    # Mark the user as not having their email address confirmed(clean up)
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.email_confirmed = False
    user.email_confirmed_on = None
    db.session.add(user)
    db.session.commit()


@pytest.fixture(scope="function")
def afterwards_reset_default_user_password():
    yield  # this is where the testing is happening!

    # Since a test using this fixture could change the password for the default
    # user, rerset the password back to the default password
    user = User.query.filter_by(email="patrick@gmail.com").first()
    user.set_password("FlaskIsAwesome123")
    db.session.add(user)
    db.session.commit()
