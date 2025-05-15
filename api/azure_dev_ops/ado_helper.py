"""Azure DevOps helper functions"""
from api.azure_dev_ops.api import ado_api
from api.utilities.retry_request import retry_request
from report.log_and_report import write_logging_error


@retry_request
def get_project_by_id_or_name(organization, project_id_or_name):
    """
    Retrieves a project from Azure DevOps by its ID or name.

    Args:
        organization (str): The Azure DevOps organization.
        project_id_or_name (str): The ID or name of the project.

    Returns:
        dict: The project details as a JSON object.

    Raises:
        HTTPError: If the API response is not successful.
    """
    response = ado_api.get_project_by_id_or_name(organization, project_id_or_name)
    if response.ok:
        return response.json()
    response.raise_for_status()


@retry_request
def get_work_item_by_id(organization, project, work_item_id):
    """
    Retrieves a work item by its ID from Azure DevOps.

    Args:
        organization (str): The name of the Azure DevOps organization.
        project (str): The name of the project.
        work_item_id (int): The ID of the work item to retrieve.

    Returns:
        dict: The JSON response containing the work item details.

    Raises:
        HTTPError: If the API request fails.
    """
    response = ado_api.get_work_item_by_id(organization, project, work_item_id)
    return response.json() if response.ok else response.raise_for_status()


@retry_request
def create_work_item(organization, project, work_item_type, body):
    """
    Creates a work item in Azure DevOps.

    Args:
        organization (str): The name of the Azure DevOps organization.
        project (str): The name of the project.
        work_item_type (str): The type of the work item.
        body (dict): The JSON body containing the details of the work item.

    Returns:
        dict: The JSON response containing the created work item.

    Raises:
        HTTPError: If the API response is not successful.
    """
    response = ado_api.create_work_item(organization, project, work_item_type, body)
    if response.ok:
        return response.json()
    write_logging_error(f"Error creating work item '{work_item_type}': {response.status_code} - {response.text}")
    return response.raise_for_status()

@retry_request
def update_work_item(organization, project, work_item_id, body):
    """
    Creates a work item in Azure DevOps.

    Args:
        organization (str): The name of the Azure DevOps organization.
        project (str): The name of the project.
        work_item_id (str): The ID of the work item to update.
        body (dict): The JSON body containing the details of the work item.

    Returns:
        dict: The JSON response containing the created work item.

    Raises:
        HTTPError: If the API response is not successful.
    """
    response = ado_api.update_work_item(organization, project, work_item_id, body)
    if response.ok:
        return response.json()
    write_logging_error(f"Error updating work item '{work_item_id}': {response.status_code} - {response.text}")
    return response.raise_for_status()


@retry_request
def get_all_work_items_in_project(organization, project, team=None):
    """
    Retrieves all work items in a project.

    Args:
        organization (str): The name of the organization.
        project (str): The name of the project.
        team (str, optional): The name of the team. Defaults to None.

    Returns:
        dict: A dict with the count ant the list of dictionaries representing the work items.

    Raises:
        HTTPError: If there is an error in the HTTP request.

    """
    if not team:
        team = f"{project} Team"
    body = {"query": f"SELECT [System.Id] FROM workitems WHERE [System.TeamProject] = '{project}'"}
    top = 100
    response = ado_api.query_by_wiql(organization, project, team, top, body)
    if response.ok:
        work_item_ids = [work_item["id"] for work_item in response.json()["workItems"]]
        if len(work_item_ids) == 0:
            return work_item_ids
        body = {"ids": work_item_ids,
                "fields": ["System.Description", "System.Title", "System.State"]}
        response = ado_api.get_work_items_batch(organization, project, body)
        return response.json() if response.ok else response.raise_for_status()
    return response.raise_for_status()
