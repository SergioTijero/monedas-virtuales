from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
