from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_type = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_nickname = db.Column(db.String(150), nullable=False)
    currency_type = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    remaining_stock = db.Column(db.Integer, nullable=False)
