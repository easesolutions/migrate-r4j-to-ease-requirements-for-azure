"""Helper functions to call the Azure DevOps REST API for Requirements."""
from api.azure_dev_ops import ado_helper
from api.azure_dev_ops.api import ease_requirements_api
from api.utilities.retry_request import retry_request
from report.log_and_report import (write_logging_server_response,
                                   write_logging_simple_message)


@retry_request
def create_single_tree_item(project_id, child_id, parent_id):
    """
    Create a single tree item.

    Args:
        project_id (str): The ID of the project.
        child_id (str): The ID of the child item.
        parent_id (str): The ID of the parent item.

    Returns:
        str: The ID of the created tree item.
    """
    tree_item = {
        "id": child_id,
        "parent": parent_id,
    }
    response = ease_requirements_api.create_single_tree_item(project_id, body=tree_item)
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        created_id = result["id"]
        write_logging_simple_message(f"Tree item created with ID: {created_id}, parent {parent_id}")
        return created_id
    else:
        response.raise_for_status()


@retry_request
def get_all_tree_items(project_id):
    """
    Get all tree items for a project.

    Args:
        project_id (str): The ID of the project.

    Returns:
        list: A list of all tree items.
    """
    response = ease_requirements_api.get_all_tree_items(project_id)
    if response.status_code == 200:
        return response.json()["value"]
    elif response.status_code == 404:
        write_logging_server_response(response, f"{response.status_code} Collection does not exist")
        return None
    else:
        response.raise_for_status()


@retry_request
def delete_single_tree_item(project_id, item_id):
    """
    Delete a single tree item.

    Args:
        project_id (str): The ID of the project.
        item_id (str): The ID of the item to delete.
    """
    response = ease_requirements_api.delete_single_tree_item(project_id, item_id)
    if response.status_code == 204:
        write_logging_simple_message(f"Tree item deleted with ID: {item_id}")
    else:
        response.raise_for_status()


@retry_request
def get_folder_work_item_type(organization, project_key):
    """
    Get the folder work item type for a project.

    Args:
        organization (str): The organization name.
        project_key (str): The key of the project.

    Returns:
        str: The folder work item type.
        response: The response of the api.
    """
    project_id = ado_helper.get_project_by_id_or_name(organization, project_key)["id"]
    response = ease_requirements_api.get_folder_work_item_type(project_id)
    if response.ok:
        folder_item_type = response.json()["value"]["folderSettings"]["folderItemType"]
        if folder_item_type != "None":
            write_logging_simple_message(f"The folder work item type is {folder_item_type}")
            return folder_item_type, response
        else:
            message = \
                "PROJECT WORK ITEM TYPES ERROR: Folder work item type not found " \
                f"on project {project_key}." \
                "\n\n If you want to continue with the migration you need to " \
                "configure Folder work item type for " \
                f"{project_key} in the Requirements settings"
            write_logging_server_response(response, message, True, AssertionError)
    else:
        message = f"ERROR: Cannot retrieve the Folder work item type on the project " \
                  f"{project_key}: {response.reason} ({response.status_code}). Please configure the Folder work item " \
                  f"type in the Requirements settings " \
                  f"(see https://easesolutions.atlassian.net/wiki/spaces/R4ADO/pages/2381283731/Getting+started)."
        write_logging_server_response(response, message, True, ConnectionError)
        if response.status_code == 500:
            write_logging_simple_message(response.content)
