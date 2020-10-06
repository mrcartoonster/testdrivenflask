# -*- coding: utf-8 -*-
from datetime import datetime

from flask import current_app

from project import bcrypt, db


class Stock(db.Model):
    """
    Class the represents a purchased stock in a portolio.

    The following attributes of a stock are stored in this table:
        stock symbol (type: string)
        number of shares (type: integer)
        purchase price (type: integer)

    Note: Due to a limitation in the data types supported by SQLite, the
    purchae price is stored as in integer:
        $24.10 -> 2410
        $100.00 -> 10000
        $87.65 -> 8765

    Note: This is why when I make my own Flask apps with dbs, I'll
    be using Postgres. Postgres as a money type!

    """

    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String, nullable=False)
    number_of_shares = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        stock_symbol: str,
        number_of_shares: str,
        purchase_price: str,
    ):
        self.stock_symbol = stock_symbol
        self.number_of_shares = int(number_of_shares)
        self.purchase_price = int(float(purchase_price) * 100)

    def __repr__(self):
        return (
            f"{self.stock_symbol} - {self.number_of_shares} "
            "shares purchased at ${self.purchase_price / 100}"
        )


class User(db.Model):
    """
    Class that represents a user of the application.

    The following attributes of a user are stored in this table:
        * email - email address of the user
        * hashed_password - hashed password (using Flask-Bcrypt)
        * registered_on - date & time tht the user registered
        * email_confirmation_sent_on - date & time that the confirmation email
            was sent
        * email_confirmed - flag indcating if the userr's email address has
            been confirmed
        * email_confirmed_on - date & time that the user's email address was
            confirmed

    REMEMBER: Never store the plaintext password in a database!

    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password_hashed = db.Column(db.String(60))
    registered_on = db.Column(db.DateTime)
    email_confirmation_sent_on = db.Column(db.DateTime)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_on = db.Column(db.DateTime)

    def __init__(
        self,
        email: str,
        password_plaintext: str,
        email_confirmation_sent_on=None,
    ):
        self.email = email
        # May have to add current_app config here
        self.password_hashed = bcrypt.generate_password_hash(
            password_plaintext,
        ).decode("utf-8")
        self.registered_on = datetime.now()
        self.confirmation_sent_on = datetime.now()
        self.email_confirmed_sent_on = datetime.now()
        self.email_confirmed = False
        self.email_confirmed_on = None

    @property
    def is_authenticated(self):
        """return True if the user has been successfully registered."""
        return True

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonoymous(self):
        """Always False, as anonymous users aren't supportted."""
        return False

    def get_id(self):
        """Return the user ID as a unicode string (`str`)."""
        return str(self.id)

    def is_password_correct(self, password_plaintext: str):
        return bcrypt.check_password_hash(
            self.password_hashed,
            password_plaintext,
        )

    def set_password(self, password_plaintext):
        self.password_hashed = bcrypt.generate_password_hash(
            password_plaintext,
            current_app.config.get("BCRYPT_LOG_ROUNDS"),
        ).decode("utf-8")

    def __repr__(self):
        return f"<User: {self.email}>"
