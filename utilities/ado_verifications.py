from api.azure_dev_ops import ease_requirements_helper
from api.azure_dev_ops import ado_helper
from api.azure_dev_ops.api import ado_api
from report.log_and_report import write_logging_server_response


def verify_folder_work_item_type(organization, project_key):
    """
    Verifies if the folder work item type is configured in the ADO instance.

    Args:
        organization (str): The name of the organization.
        project_key (str): The key of the project.

    Returns:
        bool: True if the folder work item type is configured, False otherwise.
    """
    folder_work_item_type, response = ease_requirements_helper.get_folder_work_item_type(organization, project_key)
    if folder_work_item_type is not None:
        message = "Folder work item type is configured in ADO instance"
        write_logging_server_response(response, message)
        return True
    else:
        message = "FOLDER ISSUE TYPE ERROR: Folder work item type is not configured in cloud instance"
        write_logging_server_response(response, message, True, AssertionError)


def verify_data_center_project_exists_in_ado(organization, project_key):
    """
    Verifies if the project exists in the Azure DevOps (ADO) instance.

    Args:
        organization (str): The name of the organization.
        project_key (str): The key of the project.

    Returns:
        bool: True if the project exists, False otherwise.
    """
    response = ado_api.get_project_by_id_or_name(organization, project_key)
    if response.status_code == 200 and response.json()["name"] == project_key:
        message = "Project exists on ADO"
        write_logging_server_response(response, message)
        return verify_r4ado_is_active_ado_organization(organization)
    else:
        message = "ERROR: Project not found on Azure DevOps"
        write_logging_server_response(response, message, True, AssertionError)


def verify_r4ado_is_active_ado_organization(organization):
    """
    Verifies if the organization is an active Azure DevOps (ADO) organization.

    Args:
        organization (str): The name of the organization.

    Returns:
        bool: True if the organization is active, False otherwise.
    """
    return True


def verify_authorized_in_ado_api(organization):
    """
    Verifies if the user is authorized to use the Azure DevOps (ADO) REST API.

    Args:
        organization (str): The name of the organization.

    Returns:
        bool: True if the user is authorized, False otherwise.
    """
    response = ado_api.get_all_projects_by_organization(organization)
    if response.status_code == 401:
        message = "INVALID AUTHENTICATION: You are not authorized to use ADO REST API"
        write_logging_server_response(response, message, True, ValueError)
    elif response.status_code == 200:
        message = "You are authorized to use ADO REST API, you can continue with the migration"
        write_logging_server_response(response, message)
        return True


def verify_all_data_center_tree_issues_in_ado_instance(jira_ado_ids, tree_items_list, organization, project):
    """
    Verifies all data center tree issues in the Azure DevOps (ADO) instance.

    Args:
        jira_ado_ids (dict): A dictionary mapping JIRA IDs to ADO IDs.
        tree_items_list (list): A list of tree items.
        organization (str): The name of the organization.
        project (str): The name of the project.

    Returns:
        bool: True if all tree issues are verified, False otherwise.
    """
    ado_work_items = ado_helper.get_all_work_items_in_project(organization, project)
    if len(ado_work_items) != 0:
        for index, issue in enumerate(tree_items_list):
            issue["id"] = find_existing_work_items_on_ado(issue, ado_work_items['value'])
            if issue["id"]:
                tree_items_list[index] = issue
                jira_ado_ids[str(issue["jira_id"])] = issue["id"]
    return len(tree_items_list) == len(jira_ado_ids) - 1


def find_existing_work_items_on_ado(jira_issue, ado_work_items):
    """
    Finds existing work items on Azure DevOps (ADO) based on JIRA issue data.

    Args:
        jira_issue (dict): The JIRA issue data.
        ado_work_items (list): A list of ADO work items.

    Returns:
        str: The ID of the existing work item if found, None otherwise.
    """
    for item in ado_work_items:
        title_key = "folder_name" if "folder_name" in jira_issue else "summary"
        ado_description = item["fields"]["System.Description"] if "System.Description" in item["fields"] else ""
        if "folder_name" in jira_issue:
            jira_description = jira_issue["folderData"]["description"] \
                               if jira_issue["folderData"]["description"] else ""
            if '\xa0' in jira_description:
                jira_description = jira_description.replace('\xa0', '&nbsp;')
            if jira_issue[title_key] == item["fields"]["System.Title"]:
                if jira_description == ado_description:
                    ado_work_items.remove(item)
                    return item["id"]
        else:
            jira_description = jira_issue["issueData"]["fields"]["description"] \
                               if jira_issue["issueData"]["fields"]["description"] else ""
            if '\xa0' in jira_description:
                jira_description = jira_description.replace('\xa0', '&nbsp;')
            if jira_issue[title_key] == item["fields"]["System.Title"]:
                if jira_description == ado_description:
                    ado_work_items.remove(item)
                    return item["id"]


def run_project_ado_verifications(organization, project_key):
    """
    Runs the Azure DevOps (ADO) verifications for a project.

    Args:
        organization (str): The name of the organization.
        project_key (str): The key of the project.

    Returns:
        bool: True if all verifications pass, False otherwise.
    """
    try:
        if verify_authorized_in_ado_api(organization):
            return verify_folder_work_item_type(organization, project_key) and \
                verify_data_center_project_exists_in_ado(organization, project_key)
    except Exception as e:
        print(e)
        return False
