from flask_restful import Api, Resource, reqparse
from flask import Blueprint, abort
import requests
from jira.exceptions import *

bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(bp)

issue_type_parser = reqparse.RequestParser()
issue_type_parser.add_argument("jiraUrl", type=str)

subtask_type_parser = reqparse.RequestParser()
subtask_type_parser.add_argument("jiraUrl", type=str)

JIRA_ENDPOINT = "codemaster.obss.io/jira/"


class EchoResource(Resource):
    def get(self, text):
        return text

    def put(self, text):
        return PUT_NOT_SUPPORTED


class IssueTypesResource(Resource):
    def get(self):

        try:
            args = issue_type_parser.parse_args()
            query = args["jiraUrl"] + "rest/api/2/issuetype"
        except KeyError:
            return JIRA_URL_MISSING

        res = requests.get(query)

        if res.status_code != 200:
            return JIRA_NOT_AVAILABLE
        else:
            res = res.json()



        to_return = list()
        for i in res:
            to_return.append({
                "id": i["id"],
                "description": i["description"],
                "name": i["name"],
                "subtask": i["subtask"]
            })

        return to_return

    def put(self):
        return PUT_NOT_SUPPORTED


class SubtaskTypeResource(Resource):
    def get(self):
        args = subtask_type_parser.parse_args()
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
api.add_resource(SubtaskTypeResource, "/subtasks")
