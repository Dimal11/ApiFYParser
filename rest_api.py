import json

from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from parser import Parser


class ApiParser(Resource):

    @staticmethod
    def get(company):
        parser = Parser()
        result = parser.parse(company)
        json_file = json.dumps(result, indent=1)
        return json_file


api.add_resource(ApiParser, '/<string:company>')

if __name__ == '__main__':
    app.run()
