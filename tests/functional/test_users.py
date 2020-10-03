# -*- coding: utf-8 -*-
"""Tests for user registrations."""
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from project import mail
from project.models import User


def test_get_registration_page(test_client):
    """GIVEN a Flask application configured for testing WHEN the
    '/users/register' pages is requested (GET) THEN check the respons is
    valid."""

    response = test_client.get("/users/register")
    assert response.status_code == 200
    assert b"Flask Stock Portfolio App" in response.data
    assert b"User Registration" in response.data
    assert b"Email: " in response.data
    assert b"Password: " in response.data


def test_valid_registration(test_client):
    """GIVEN a Flask application configured for testing WHEN the
    '/users/registr' page is posted to (POST) with valid data THEN check
    the response is valid and the user is registered."""

    with mail.record_messages() as outbox:
        response = test_client.post(
            "/users/register",
            data={
                "email": "patrick@email.com",
                "password": "FlaskIsAwesome123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Thanks for registering, patrick@email.com" in response.data
        assert b"Flask Stock Portfolio App" in response.data
        assert len(outbox) == 1
        assert (
            outbox[0].subject
            == "Flask Stock Portfolio App - Confirm Your Email Address"
        )
        assert outbox[0].sender == "mrcartoonster@gmail.com"
        assert outbox[0].recipients[0] == "patrick@email.com"
        assert "http://localhost/users/confirm/" in outbox[0].html


def test_invalid_registration(test_client):
    """GIVEN a Flask application configured for testing WHEN the
    '/usrs/register' page is posted to (POST) with invalid data (missing
    password) THEN check an error message is returned to the user."""

    response = test_client.post(
        "/users/register",
        data={"email": "patrick2@email.com", "password": ""},  # No password
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Thanks for registering, patrick2@email.com!" not in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"[This field is required.]" in response.data


def test_duplicate_registration(test_client):
    """GIVEN a Flask application configured for testing WHEN the
    '/users/register' page is posted to (POST) with the email address
    for an existing user THEN check an error message is returned to the
    user."""

    test_client.post(
        "/users/register",
        data={"email": "patrick@hotmail.com", "password": "FlaskIsAwesome123"},
        follow_redirects=True,
    )

    response = test_client.post(
        "/users/register",
        data={
            "email": "patrick@hotmail.com",  # Duplicate email address
            "password": "FlaskIsStillGreat!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Thank for registering, partick@hotmail.com!" not in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert (
        b"ERROR! Email (patrick@hotmail.com) already exists." in response.data
    )


def test_get_login_page(test_client):
    """GIVEN a Flask application WHEN the '/users/login' page is
    requested (GET) THEN check the response is valid."""
    response = test_client.get("/users/login")
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data
    assert b"Login" in response.data


def test_valid_login_and_logout(test_client, register_default_user):
    """GIVEN a Flask application WHEN the '/users/login' page is posted
    to (POST) with valid credentials THEN check the response is
    valid."""
    response = test_client.post(
        "/users/login",
        data={"email": "patrick@gmail.com", "password": "FlaskIsAwesome123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Thanks for logging in, patrick@gmail.com!" in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Please log in to access this page." not in response.data

    """
    GIVEN a Flask application
    WHEN the '/users/logout' page is requested (GET) for a logged in user
    THEN check the response is valid
    """
    response = test_client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Please log in to access this page." not in response.data


def test_invalid_login(test_client, register_default_user):
    """GIVEN a Flask application WHEN the '/users/login' page is posted
    to (POST) with invalid credentials (incorrect password) THEN check
    an error message is returned to the user."""
    response = test_client.post(
        "/users/login",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsNotAwesome",
        },  # Incorrect!
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"ERROR! Incorrect login credentials." in response.data
    assert b"Flask Stock Portfolio App" in response.data


def test_valid_login_when_logged_in_already(
    test_client,
    register_default_user,
):
    """GIVEN a Flask application WHEN the '/users/login' page is posted
    to (POST) with value credentials for a user already logged in THEN
    check a warning is returned to the user."""
    test_client.post(
        "/users/login",
        data={"email": "patrick@gmail.com", "password": "FlaskIsAwesome123"},
        follow_redirects=True,
    )
    response = test_client.post(
        "/users/login",
        data={"email": "patrick@gmail.com", "password": "FlaskIsAwesome123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Already logged in!" in response.data
    assert b"Flask Stock Portfolio App" in response.data


def test_invalid_logout(test_client):
    """GIVEN a Flask application WHEN the '/users/logout' page is posted
    to (POST) THEN check that a 405 error is returned."""
    response = test_client.post("/users/logout", follow_redirects=True)
    assert response.status_code == 405
    assert b"Goodbye!" not in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Method Not Allowed" in response.data


def test_invalid_logout_not_logged_in(test_client):
    """GIVEN a Flask application WHEN the '/users/logout' page is
    requested (GET) when the user is not logged in THEN check that the
    user is redirected to the login page."""
    test_client.get(
        "/users/logout",
        follow_redirects=True,
    )  # Double-check that there are no logged in users!
    response = test_client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" not in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Login" in response.data
    assert b"Please log in to access this page." in response.data


def test_user_profile_logged_in(test_client, log_in_default_user):
    """GIVEN a Flask application WHEN the '/users/profile' page is
    requested (GET) when the user is logged in THEN check that the
    profile for the current user is displayed."""
    response = test_client.get("/users/profile")
    assert response.status_code == 200
    assert b"Flask Stock Portfolio App" in response.data
    assert b"User Profile" in response.data
    assert b"Email: patrick@gmail.com" in response.data


def test_user_profile_not_logged_in(test_client):
    """GIVEN a Flask application WHEN the '/users/profile' page is
    requested (GET) when the user is NOT logged in THEN check that the
    user is redirected to the login page."""
    response = test_client.get("/users/profile", follow_redirects=True)
    assert response.status_code == 200
    assert b"Flask Stock Portfolio App" in response.data
    assert b"User Profile!" not in response.data
    assert b"Email: patrick@gmail.com" not in response.data
    assert b"Please log in to access this page." in response.data


def test_login_with_next_valid_path(test_client, register_default_user):
    """GIVEN a Flask appliction WHEN the
    'users/login?next=%2Fusers%Fprofile' pages is posted to (POST) with
    a valid user login THEN check that the user is redirected to the
    user profile page."""

    response = test_client.post(
        "users/login?next=%2Fusers%2Fprofile",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Flask Stock Portfolio App" in response.data
    assert b"User Profile" in response.data
    assert b"Email: patrick@gmail.com" in response.data

    # Log out the user - Clean up!
    test_client.get("/users/logout", follow_redirects=True)


def test_login_with_next_invalid_path(test_client, register_default_user):
    """GIVEN a Flask application WHEN the
    'users/login?next=http://www.badsite.com' page is posted to (POST)
    with a valid user login THEN check that a 40 (Bad Request) error is
    returned."""

    response = test_client.post(
        "users/login?next=http://www.badsite.com",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert b"User Profile" not in response.data
    assert b"Email: patrick@gmail.com" not in response.data


def test_confirm_email_valid(test_client):
    """GIVEN a Flask application WHEN the '/users/confirm/<token>' page
    is requested (GET) with valid data THEN check that the user's email
    address is marked as confirmed."""

    # Create the unique token for confirmating a user's email address
    confirm_serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
    )
    token = confirm_serializer.dumps(
        "patrick@gmail.com",
        salt="email-confirmation-salt",
    )

    response = test_client.get("/users/confirm" + token, follow_redirects=True)
    assert response.status_code == 200
    assert b"Thank you for confirming your email address!" in response.data
    user = User.query.filter_by(email="patrick@gmail.com").first()
    assert user.email_confirmed


def test_confirm_email_already_confirmed(test_client):
    """GIVEN a flask appliction - WHEN the '/users/confirm/<token>' page
    is requested (GET) with valid data but the user's emails is already
    confirmed - THEN check that the user's email address is marked as
    confirmed."""

    # Create the unique token for confirming a user's email address
    confirm_serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
    )
    token = confirm_serializer.dumps(
        "patrick@gmail.com",
        salt="email-confirmation-salt",
    )

    # Confirm the user's email address
    test_client.get("/users/confirm" + token, follow_redirects=True)

    # Process a valid confirmation link for a user that has their email address
    # already confirmed.
    response = test_client.get(
        "/users/confirm/" + token,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account already confirmed." in response.data
    user = User.query.filter_by(email="patrick@gmai.com").first()
    assert user.email_confirmed


def test_confirm_email_invalid(test_client):
    """GIVEN a Flask application WHEN the '/users/confirm/<token>' page
    is requested (GET) with invalid data THEN check that the link was
    not accepted."""

    response = test_client.get(
        "/users/confirm/bad_confirmation_link",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"The confirmation link is invalid or has expired." in response.data
