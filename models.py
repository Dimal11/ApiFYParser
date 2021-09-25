from rest_api import db


class DataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)

