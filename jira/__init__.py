from flask import Flask
from jira import api


def create_app():

    app = Flask(__name__)

    app.config["DEBUG"] = True

    def index_view():
        return "Hello"

    app.add_url_rule("/", view_func=index_view)

    app.register_blueprint(api.bp)

    return app



