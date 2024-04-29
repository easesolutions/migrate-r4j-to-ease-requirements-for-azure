
"""Jira helper functions"""
from api.data_center.api import jira_api
from api.utilities.retry_request import retry_request


@retry_request
def get_issue_by_key(issue_key):
    """
    Retrieves an issue from Jira based on the provided issue key.

    Args:
        issue_key (str): The key of the issue to retrieve.

    Returns:
        dict: The JSON response containing the issue details.
    """
    response = jira_api.get_issue_by_key(issue_key).json()
    return response


@retry_request
def get_all_projects():
    """
    Retrieves a project from Jira based on the provided project ID or key.

    Returns:
        dict: The JSON response containing the project details.
    """
    response = jira_api.get_all_projects().json()
    return response


@retry_request
def get_project_by_name(project_name):
    """
    Retrieves a project from Jira based on the provided project ID or key.

    Args:
        project_name (str): The ID or key of the project to retrieve.

    Returns:
        dict: The JSON response containing the project details.
    """
    response = get_all_projects()
    for project in response:
        if project["name"] == project_name:
            return project
    raise ValueError(f"Project with name {project_name} not found")


@retry_request
def get_project_by_id_or_key(project_id_or_key):
    """
    Retrieves a project from Jira based on the provided project ID or key.

    Args:
        project_id_or_key (str): The ID or key of the project to retrieve.

    Returns:
        dict: The JSON response containing the project details.
    """
    response = jira_api.get_project_by_id_or_key(project_id_or_key).json()
    return response


@retry_request
def get_all_issues_in_project_by_project_key(project_key):
    """
    Retrieves all issues in a project from Jira based on the provided project key.

    Args:
        project_key (str): The key of the project to retrieve issues from.

    Returns:
        dict: The JSON response containing the list of issues in the project.
    """
    response = jira_api.get_all_issues_in_project_by_project_key(project_key).json()
    return response
