
def parse_issue_task2(issue):
    """ Take issue and transform into desired format """
    res = {
        "id": issue["id"],
        "description": issue["description"],
        "name": issue["name"],
        "subtask": issue["subtask"]
    }
    return res


def task3_issue_helper(issue):

    parsed_issue = {
        "id": issue["id"],
        "key": issue["key"],
        "fields": {
            "assignee": {
                "name": issue["fields"]["assignee"]["name"],
                "key": issue["fields"]["assignee"]["key"],
                "emailAddress": issue["fields"]["assignee"]["emailAddress"],
                "displayName": issue["fields"]["assignee"]["displayName"]
            } if issue["fields"]["assignee"] else None,
            "reporter": {
                "name": issue["fields"]["reporter"]["name"],
                "key": issue["fields"]["reporter"]["key"],
                "emailAddress": issue["fields"]["reporter"]["emailAddress"],
                "displayName": issue["fields"]["reporter"]["displayName"]
            } if issue["fields"]["reporter"] else None,
            "project": {
                "id": issue["fields"]["project"]["id"],
                "key": issue["fields"]["project"]["key"],
                "name": issue["fields"]["project"]["name"],
            } if issue["fields"]["project"] else None
        }
    }

    return parsed_issue