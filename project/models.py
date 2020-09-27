# -*- coding: utf-8 -*-
from dataclasses import dataclass

from project import bcrypt, current_app, db


class Stock(db.Model):
    """Class the represents a purchased stock in a portolio.

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


@dataclass
class User(db.Model):
    """Class that represents a user of the applications.

    The following attributes of a user are stored in this table:
        * email -email address of the user
        * hashed password - hashed password (using Flask-Bcrypt)

    REMEMBER: Never store the plaintext password in a dtabase!
    """

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String, unique=True)
    password_hashed = db.Column(db.String(60))

    def __init__(self, email: str, password_plaintext: str):
        self.email = email
        self.password_hashed = bcrypt.generate_password_hash(
            password_plaintext,
            current_app.config.gete("BCRYPT_LOG_ROUNDS"),
        ).decode("utf-8")

    def is_password_correct(self, password_plaintext: str):
        return bcrypt.check_password_hash(
            self.password_hashed,
            password_plaintext,
        )
