#!/usr/bin/python3
"""The Flask application module"""
from os import getenv

from flask import Flask, jsonify, make_response
from flask_cors import CORS
from flasgger import Swagger

from api.v1.views import app_views
from models import storage

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/*": {"origins": "0.0.0.0"}})


@app.errorhandler(404)
def not_found(error):
    """
    Handler that returns a JSON-formatted 404 status code response.
    """
    return make_response(jsonify({"error": "Not found"}), 404)


@app.teardown_appcontext
def close_storage(obj):
    """Method to close the storage"""
    storage.close()


app.config['SWAGGER'] = {
    'title': 'AirBnB clone - RESTful API',
    'description': 'Python back-end API webserver Flask',
    'uiversion': 3}

Swagger(app)


if __name__ == "__main__":
    host = getenv('HBNB_API_HOST', default='0.0.0.0')
    port = getenv('HBNB_API_PORT', default='5000')

    app.run(host=host, port=int(port), threaded=True)
