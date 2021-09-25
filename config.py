import os
import pathlib
import psycopg2


def get_path_to_data_folder():
    return pathlib.Path(__file__).parent.joinpath("JSON Files")


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgresql+psycopg2://postgres:dl110987DL@localhost:5432/parser'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
