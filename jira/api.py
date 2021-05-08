from flask_restful import Api, Resource, reqparse
from flask import Blueprint, abort, make_response, request
import requests
from jira.exceptions import *

bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(bp)

issue_type_parser = reqparse.RequestParser()
issue_type_parser.add_argument("jiraUrl", type=str)

subtask_type_parser = reqparse.RequestParser()
subtask_type_parser.add_argument("jiraUrl", type=str)
subtask_type_parser.add_argument("projectId", type=str)

find_top_n_parser = reqparse.RequestParser()
find_top_n_parser.add_argument("jiraUrl", type=str, location='args')
find_top_n_parser.add_argument("topn", type=int, location='args')
#find_top_n_parser.add_argument('project_ids', type=list, location='form')

project_parser = reqparse.RequestParser()
project_parser.add_argument("jiraUrl", type=str, location='args')
project_parser.add_argument("minn", type=int, location='args')
project_parser.add_argument("topm", type=int, location='args')

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


class FindTopNUsersResource(Resource):

    def post(self):

        project_ids = request.json
        args = find_top_n_parser.parse_args()
        if args["jiraUrl"] is None:
            return JIRA_URL_MISSING

        appendix = "rest/api/2/search?jql=project={p_id}&maxResults=9999999"

        names = {}

        for p_id in project_ids:
            res = requests.get(args["jiraUrl"] + appendix.format(p_id=p_id))

            if res.status_code != 200:
                return JIRA_NOT_AVAILABLE
            else:
                res = res.json()

            issues = res["issues"]

            for iss in issues:
                if iss["fields"]["assignee"]:
                    name  = iss["fields"]["assignee"]["name"]  # extract name form issue
                    # find name and inc value
                    if name in names.keys():
                        names[name]["issueCount"] += 1
                    else:
                        names[name] = {
                            "name": iss["fields"]["assignee"]["name"] if iss["fields"]["assignee"] else None,
                            "key": iss["fields"]["assignee"]["key"] if iss["fields"]["assignee"] else None,
                            "emailAddress": iss["fields"]["assignee"]["emailAddress"] if iss["fields"]["assignee"] else None,
                            "displayName": iss["fields"]["assignee"]["displayName"] if iss["fields"]["assignee"] else None,
                            "issueCount": 1
                        }

        all_users = list(names.values())
        topn = sorted(all_users, key=lambda x: x["issueCount"], reverse=True)[:args["topn"]]

        return topn

    def put(self, text):
        return PUT_NOT_SUPPORTED

"""
class TopMProjectsMinNIssues(Resource):

    def post(self):
        users = request.json
        args = project_parser.parse_args()
        if args["jiraUrl"] is None:
            return JIRA_URL_MISSING

        appendix = "rest/api/2/search?jql=project={p_id}&maxResults=9999999"

        names = {}
        return {}, 200
    
    def put(self, text):
        return PUT_NOT_SUPPORTED
"""

api.add_resource(EchoResource, "/echo/<text>")
api.add_resource(IssueTypesResource, "/issuetypes")
api.add_resource(SubtaskTypeResource, "/issues/subtasks")
api.add_resource(FindTopNUsersResource, "/users/find-top-n-users")
#api.add_resource(TopMProjectsMinNIssues, "/projects/find-min-n-issues")

