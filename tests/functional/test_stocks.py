# -*- coding: utf-8 -*-


def test_get_add_stock_page(test_client, log_in_default_user):
    """GIVEN a Flask application WHEN the '/add_stock' page is requested
    (GET) THEN check the response is valid."""
    response = test_client.get("/add_stock")
    assert response.status_code == 200
    assert b"Flask Stock Portfolio App" in response.data
    assert b"Add a Stock:" in response.data
    assert b"Stock Symbol (required):" in response.data
    assert b"Number of Shares (required):" in response.data
    assert b"Purchase Price (required) ($):" in response.data
    assert b"Purchase Date" in response.data


def test_post_add_stock_page(test_client, log_in_default_user):
    """GIVEN a Flask application WHEN the '/add_stock' page is posted
    (POST) THEN check that the user is redirected to the '/list_stocks'
    page."""

    response = test_client.post(
        "/add_stock",
        data={
            "stock_symbol": "AAPL",
            "number_of_shares": "23",
            "purchase_price": "432.17",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"List of Stocks" in response.data
    assert b"Stock Symbol" in response.data
    assert b"Number of Share" in response.data
    assert b"Share Price" in response.data
    assert b"AAPL" in response.data
    assert b"23" in response.data
    assert b"432.17" in response.data
    assert b"Added new stock (AAPL)!" in response.data


def test_get_add_stock_page_not_logged_in(test_client):
    """GIVEN a Flask application WHEN the '/add_stock' page is requested
    (GET) when the user is not logged in THEN check that the user is
    redirected to the login page."""
    response = test_client.get("/add_stock", follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a Stock" not in response.data


def test_post_add_stock_page_not_logged_in(test_client):
    """GIVEN a Flask application WHEN the '/add_stock' page is posted to
    (POST) when the user is not logged in THEN check that the user is
    redirected to the login page."""
    response = test_client.post(
        "/add_stock",
        data={
            "stock_symbol": "AAPL",
            "number_of_shares": "23",
            "purchase_price": "432.17",
            "purchase_date": "07/24/2020",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"List of Stocks:" not in response.data
    assert b"Added new stock (AAPL)!" not in response.data
    assert b"Please log in to access this page." in response.data
    assert b"Please log in to access this page." in response.data
