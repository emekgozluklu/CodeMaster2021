from datetime import datetime

today = datetime.today().strftime("%Y-%m-%d")

USER_NOT_FOUND = {
    "timestamp": today,
    "status": 500,
    "errors": "users not found"
}

USER_INFO_REQUIRED = {
    "timestamp": today,
    "status": 400,
    "errors": "Required request body is missing:"
}

JIRA_URL_MISSING = {
    "timestamp": today,
    "status": 400,
    "errors": "Required String parameter 'jiraUrl' is not present"
}

JIRA_NOT_AVAILABLE = {
    "timestamp": today,
    "status": 500,
    "errors": "Jira is not available"
}

GET_NOT_SUPPORTED = {
    "timestamp": today,
    "status": 405,
    "errors": "Request method 'GET' not supported"
}

PUT_NOT_SUPPORTED = {
    "timestamp": today,
    "status": 405,
    "errors": "Request method 'PUT' not supported"
}
