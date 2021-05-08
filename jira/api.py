from flask_restful import Api, Resource, reqparse
from flask import Blueprint, abort, make_response
import requests
from jira.exceptions import *

bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(bp)

issue_type_parser = reqparse.RequestParser()
issue_type_parser.add_argument("jiraUrl", type=str)

subtask_type_parser = reqparse.RequestParser()
subtask_type_parser.add_argument("jiraUrl", type=str)
subtask_type_parser.add_argument("projectId", type=str)


JIRA_ENDPOINT = "codemaster.obss.io/jira/"


class EchoResource(Resource):
    def get(self, text):
        response = make_response(text, 200)
        response.mimetype = "text/plain"
        return response

    def put(self, text):
        return PUT_NOT_SUPPORTED


class IssueTypesResource(Resource):

    def get(self):

        args = issue_type_parser.parse_args()
        if args["jiraUrl"] is None:
            return JIRA_URL_MISSING

        query = args["jiraUrl"] + "rest/api/2/issuetype"
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

        if args["jiraUrl"] is None:
            return JIRA_URL_MISSING

        query = args["jiraUrl"] + "rest/api/2/search?jql=project={p_id}" + "&maxResults=9999999"
        p_id = args["projectId"]

        res = requests.get(query.format(p_id=p_id))

        if res.status_code != 200:
            return JIRA_NOT_AVAILABLE
        else:
            res = res.json()

        issues = res["issues"]
        if issues is None:
            return JIRA_URL_MISSING

        to_return = list()
        for issue in issues:

            if issue["fields"]["issuetype"]["subtask"]:
                new_iss = {
                    "id": issue["id"],
                    "key": issue["key"],
                    "fields": {
                        "assignee": {
                            "name": issue["fields"]["assignee"]["name"] if issue["fields"]["assignee"] else None,
                            "key": issue["fields"]["assignee"]["key"] if issue["fields"]["assignee"] else None,
                            "emailAddress": issue["fields"]["assignee"]["emailAddress"] if issue["fields"]["assignee"] else None,
                            "displayName": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else None
                        } if issue["fields"]["assignee"] else None,
                        "reporter": {
                            "name": issue["fields"]["reporter"]["name"],
                            "key": issue["fields"]["reporter"]["key"],
                            "emailAddress": issue["fields"]["reporter"]["emailAddress"],
                            "displayName": issue["fields"]["reporter"]["displayName"]
                        },
                        "project": {
                            "id": issue["fields"]["project"]["id"],
                            "key": issue["fields"]["project"]["key"],
                            "name": issue["fields"]["project"]["name"],
                        }
                    }
                }
                to_return.append(new_iss)

        return {"issues": to_return}


    def put(self):
        return PUT_NOT_SUPPORTED


api.add_resource(EchoResource, "/echo/<text>")
api.add_resource(IssueTypesResource, "/issuetypes")
api.add_resource(SubtaskTypeResource, "/issues/subtasks")
