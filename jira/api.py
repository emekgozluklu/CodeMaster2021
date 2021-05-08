from flask_restful import Api, Resource, reqparse
from flask import Blueprint, make_response, request
from jira.utils import *
from jira.exceptions import *
import requests

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
        return PUT_NOT_SUPPORTED, 405


class IssueTypesResource(Resource):
    def get(self):
        args = issue_type_parser.parse_args()

        if args["jiraUrl"] is None or args["jiraUrl"] == "":
            return JIRA_URL_MISSING, 400

        query = args["jiraUrl"] + "rest/api/2/issuetype"
        res = requests.get(query)

        if res.status_code != 200:
            return JIRA_NOT_AVAILABLE, 500

        data = res.json()
        parsed_issues = list()

        for issue in data:
            parsed_issues.append(parse_issue_task2(issue))

        return parsed_issues

    def put(self):
        return PUT_NOT_SUPPORTED, 405


class SubtaskTypeResource(Resource):

    def get(self):
        args = subtask_type_parser.parse_args()

        if args["jiraUrl"] is None or args["jiraUrl"] == "":
            return JIRA_URL_MISSING, 400

        query = args["jiraUrl"] + "rest/api/2/search?jql=project={p_id}&maxResults=9999999"
        project_id = args["projectId"]
        res = requests.get(query.format(p_id=project_id))

        if res.status_code != 200:
            return JIRA_NOT_AVAILABLE, 500

        data = res.json()
        issues = data["issues"]

        to_return = list()
        for issue in issues:
            if issue["fields"]["issuetype"]["subtask"]:
                to_return.append(task3_issue_helper(issue))

        return {"issues": to_return}

    def put(self):
        return PUT_NOT_SUPPORTED, 405


class FindTopNUsersResource(Resource):

    def get(self):
        return GET_NOT_SUPPORTED, 405

    def post(self):

        if request.data:
            project_ids = request.get_json()
        else:
            project_ids = None

        args = find_top_n_parser.parse_args()

        if args["jiraUrl"] is None:
            return JIRA_URL_MISSING, 400

        appendix = "rest/api/2/search?jql=project={p_id}&maxResults=9999999"

        names = {}

        for p_id in project_ids:
            res = requests.get(args["jiraUrl"] + appendix.format(p_id=p_id))

            if res.status_code != 200:
                return JIRA_NOT_AVAILABLE, 500
            else:
                res = res.json()

            issues = res["issues"]

            for iss in issues:
                if iss["fields"]["assignee"]:
                    key = iss["fields"]["assignee"]["key"]  # extract name form issue
                    # find name and inc value
                    if key in names.keys():
                        names[key]["issueCount"] += 1
                    else:
                        names[key] = {
                            "name": iss["fields"]["assignee"]["name"] if iss["fields"]["assignee"] else None,
                            "key": iss["fields"]["assignee"]["key"] if iss["fields"]["assignee"] else None,
                            "emailAddress": iss["fields"]["assignee"]["emailAddress"] if iss["fields"]["assignee"] else None,
                            "displayName": iss["fields"]["assignee"]["displayName"] if iss["fields"]["assignee"] else None,
                            "issueCount": 1
                        }

        all_users = list(names.values())
        topn = sorted(all_users, key=lambda x: x["issueCount"], reverse=True)[:args["topn"]]

        return topn

    def put(self):
        return PUT_NOT_SUPPORTED, 405


class TopMProjectsMinNIssues(Resource):

    def get(self):
        return GET_NOT_SUPPORTED, 405

    def post(self):
        if request.data:
            users = request.get_json()
        else:
            users = None

        args = project_parser.parse_args()

        if "jiraUrl" not in request.args:
            return JIRA_URL_MISSING, 400

        if users is None:
            return USER_INFO_REQUIRED, 400

        if len(users) == 0:
            return USER_NOT_FOUND, 500

        appendix = "rest/api/2/search?jql=assignee={assignee}&maxResults=9999999"

        projects = {}

        for user in users:

            try:
                res = requests.get(args["jiraUrl"] + appendix.format(assignee=user))
                if res.status_code != 200:
                    return JIRA_NOT_AVAILABLE, 500

                issues = res.json()["issues"]
            except requests.exceptions.MissingSchema:
                return JIRA_NOT_AVAILABLE, 500

            minn = args["minn"]
            if args["minn"] is None:
                minn = 5

            topm = args["topm"]
            if args["topm"] is None:
                topm = 10

            for iss in issues:
                if iss["fields"]["project"]:
                    key = iss["fields"]["project"]["key"]
                    if key in projects.keys():
                        projects[key]["issueCount"] += 1
                    else:
                        projects[key] = {
                            "id": iss["fields"]["project"]["id"],
                            "key": iss["fields"]["project"]["key"],
                            "name": iss["fields"]["project"]["name"],
                            "issueCount": 1
                        }
        all_projects = list(projects.values())
        topm_projects = sorted(all_projects, key=lambda x: x["issueCount"], reverse=True)[:topm]

        to_ret = list()

        for i in range(len(topm_projects)):
            if topm_projects[i]["issueCount"] >= minn:
                to_ret.append(topm_projects[i])
            else:
                break

        return to_ret
    
    def put(self):
        return PUT_NOT_SUPPORTED, 405


api.add_resource(EchoResource, "/echo/<text>")
api.add_resource(IssueTypesResource, "/issuetypes")
api.add_resource(SubtaskTypeResource, "/issues/subtasks")
api.add_resource(FindTopNUsersResource, "/users/find-top-n-users")
api.add_resource(TopMProjectsMinNIssues, "/projects/find-min-n-issues")
