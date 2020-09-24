# -*- coding: utf-8 -*-
"""This file (test_models.py) contains the unit tests for the models.py
file."""
import pytest

from project.models import Stock


def test_new_stock():
    """GIVEN a Stock model WHEN a new Stock object is created THEN check the
    symbol, number of shares, and purchase price fields are defined
    corrrectly."""

    stock = Stock("AAPL", "16", "406.78")
    assert stock.stock_symbol == "AAPL"
    assert stock.number_of_shares == 16
    assert stock.purchase_price == 40678
