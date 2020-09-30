# -*- coding: utf-8 -*-
"""Tests for user registrations."""


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
    '/users/registr' page is posted to (POST) with valid data THEN check the
    response is valid and the user is registered."""

    response = test_client.post(
        "/users/register",
        data={"email": "patrick@email.com", "password": "FlaskIsAwesome123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Thanks for registering, patrick@email.com" in response.data
    assert b"Flask Stock Portfolio App" in response.data


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
    '/users/register' page is posted to (POST) with the email address for an
    existing user THEN check an error message is returned to the user."""

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
    """GIVEN a Flask application WHEN the '/users/login' page is requested
    (GET) THEN check the response is valid."""

    response = test_client.get("/users/login")
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data
    assert b"Login" in response.data


def test_valid_login_and_logout(test_client, register_default_user):
    """GIVEN a Flask application WHEN the '/users/login' page is posted to
    (POST) with valid credentials THEN check the response is valid."""

    response = test_client(
        "users/login",
        data={
            "email": "patrick@gmail.com",
            "password": "FaskIsAwesome123",
        },
    )
    assert response.status_code == 200
    assert b"Thanks for logging in, patrick@gmail.com!" in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Please log in to access this page." not in response.data

    """
    GIVEN a Flask application
    WHEN the '/users/logout' page is request (GET) for a logged in user
    THEN check response is valid
    """

    response = test_client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Please log in to access this page." not in response.data


def test_invalid_login(test_client, register_default_user):
    """GIVEN a Flask application WHEN the '/users/login' page is posted to
    (POST) with invalid credentials (incorrect password) THEN check an error
    message is returned to the user."""

    response = test_client.post(
        "users/login",
        data={"email": "patrick@gmail.com", "password": "FlaskIsNotAwesome"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"ERROR! Incorrect login credentials." in response.data
    assert b"Flask Stock Portfolio App" in response.data


def test_valid_login_when_logged_in_already(
    test_client,
    register_default_user,
):
    """GIVEN a Flask application WHEN the '/users/login' page is posted to
    (POST) with value credentials for a user already logged in THEN check a
    warning is returned to the user."""

    test_client.post(
        "users/login",
        data={
            "email": "patrick@gmail.com",
            "password": "FlaskIsAwesome123",
        },
        follow_redirects=True,
    )

    response = test_client.post(
        "/users/login",
        data={"email": "patrick@gmail.com", "password": "FlaskIsAwesome"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Already logged in!" in response.data
    assert b"Flask Stock Portfolio App" in response.data


def test_invalid_logout(test_client):
    """GIVEN a Flask application WHEN the '/users/logout' page is posted to
    (POST) THEN check that a 405 error is returned."""

    response = test_client.post("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" not in response.data
    assert b"Flask Stock Portfolio" in response.data
    assert b"Metod Not Allowed" in response.data


def test_invalid_logout_not_logged_in(test_client):
    """GIVEN a Flask application WHEN the '/users/logout' page is requested
    (GET) when the user is not logged in THEN check that the user is redirected
    to tht login page."""

    test_client.get("/users/logout", follow_redirects=True)
    response = test_client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" not in response.data
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Login" in response.data
    assert b"Please log in to access this page." in response.data