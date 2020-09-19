# -*- coding: utf-8 -*-
"""The sotck blueprint handles the user management for this appliction.

Specifically, this blueprint allows for user to add, edit, and delete
stock data from their portfolio.
"""
from flask import Blueprint

stocks_blueprint = Blueprint("stocks", __name__, template_folder="templates")
