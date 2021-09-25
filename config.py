import os
import psycopg2

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgresql+psycopg2://postgres:dl110987DL@localhost:5432/parser'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
