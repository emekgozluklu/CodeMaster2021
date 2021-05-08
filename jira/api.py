from flask_restful import Api, Resource, reqparse
from flask import Blueprint, abort
import requests

bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(bp)

issue_type_parser = reqparse.RequestParser()
issue_type_parser.add_argument("jiraUrl", type=str)

JIRA_ENDPOINT = "codemaster.obss.io/jira/"


class EchoResource(Resource):
    def get(self, text):
        return text


class IssueTypesResource(Resource):
    def get(self):
        args = issue_type_parser.parse_args()
        query = args["jiraUrl"] + "rest/api/2/issuetype"

        res = requests.get(query).json()

        to_return = list()
        for i in res:
            to_return.append({
                "id": i["id"],
                "description": i["description"],
                "name": i["name"],
                "subtask": i["subtask"]
            })

        return to_return


api.add_resource(EchoResource, "/echo/<text>")
api.add_resource(IssueTypesResource, "/issuetypes")
