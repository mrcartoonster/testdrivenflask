# -*- coding: utf-8 -*-
import pytest

from project import create_app


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app("flask_test.cfg")
    flask_app.config.form_object("config.TestingConfig")

    # Create a test client using the Flask application configured for testing
    testing_client = flask_app.test_client()

    return testing_client
