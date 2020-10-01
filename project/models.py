# -*- coding: utf-8 -*-
from project import bcrypt, db


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


class User(db.Model):
    """Class that represents a user of the application.

    The following attributes of a user are stored in this table:
        * email - email address of the user
        * hashed password - hashed password (using Flask-Bcrypt)

    REMEMBER: Never store the plaintext password in a database!

    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password_hashed = db.Column(db.String(60))

    def __init__(self, email: str, password_plaintext: str):
        self.email = email
        # May have to add current_app config here
        self.password_hashed = bcrypt.generate_password_hash(
            password_plaintext,
        ).decode("utf-8")

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

    def __repr__(self):
        return f"<User: {self.email}>"
