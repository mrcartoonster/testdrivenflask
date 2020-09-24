# -*- coding: utf-8 -*-
import pytest

from project import create_app, db
from project.models import Stock


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config.from_object("config.TestingConfig")

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
    stock = Stock("AAPL", "16", "406.78")
    return stock
