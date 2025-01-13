from api.azure_dev_ops.ado_helper import create_work_item
from config.config import ADO_ENV


def process_data_to_create_work_item(data, project_key):
    """
    Create the body to create the Work Item on the Azure DevOps side.

    Args:
        data (dict): The folder/issue data retrieved from Jira DC.
        project_key (str): The key of the project.

    Returns:
        dict: The body in json-patch+json format necessary to create the folder as a Work Item
    """
    issue_type = "Folder" if "folder" in data else data["issueData"]['fields']['issuetype']['name']     
    work_item_type = ADO_ENV.issue_type_map[issue_type] if issue_type in ADO_ENV.issue_type_map else issue_type
    extracted_info = {"organization": ADO_ENV.organization, "project": project_key, 'work_item_type': work_item_type,
                      "body": []}
    if "folder" in data:
        data = data["folderData"]
        description = data['description'] if data['description'] is not None else ""
        extracted_info['body'].append({"op": "add", "path": "/fields/System.Description", "from": None,
                                       "value": description})
        extracted_info['body'].append({"op": "add", "path": "/fields/System.Title", "from": None,
                                       "value": data['name']})
        return extracted_info
    else:
        data = data["issueData"]
        description = data['fields']['description'] if data['fields']['description'] is not None else ""
        extracted_info['body'].append({"op": "add", "path": "/fields/System.Description", "from": None,
                                       "value": description})
        extracted_info['body'].append({"op": "add", "path": "/fields/System.Title", "from": None,
                                       "value": data['fields']['summary']})
        
        '''The state value is mapped to the Azure DevOps state value, if the state value is not in the map, it will be used as is'''
        state_value = data['fields']['status']['name']
        if state_value in ADO_ENV.status_map:
            state_value = ADO_ENV.status_map[state_value]

        extracted_info['body'].append({"op": "add", "path": "/fields/System.State", "from": None,
                                       "value": state_value})

        return extracted_info


def create_work_items_on_ado(tree_items_list, jira_ado_ids, folder_type, project_key):
    """
    Create Work Items and populate the jira_ado_ids with the ids of the Work Items created.

    Args:
        tree_items_list (list): List with all the issues and folders data.
        jira_ado_ids: (list): A list to return the ids of the created Work Items.
        folder_type (str): The issue data retrieved from Jira DC.
        project_key (str): The key of the project.
    """
    ADO_ENV.issue_type_map["Folder"] = folder_type
    for index, issue in enumerate(tree_items_list):
        if "id" not in issue or not issue["id"]:
            work_item = process_data_to_create_work_item(issue, project_key)
            issue["id"] = create_work_item(work_item["organization"], work_item["project"], work_item["work_item_type"],
                                           work_item["body"])["id"]
            tree_items_list[index] = issue
            jira_ado_ids[str(issue["jira_id"])] = issue["id"]


def replace_tree_issues_data_with_jira_issue_data(tree_items_list, project_issues):
    """
    Replace the R4J tree issues data with the jira issue data

    Args:
        tree_items_list (list): List with all the issues and folders data.
        project_issues: (list): A list all the issues in the project, with all its information
        like summary, description, and status.
    """
    for index, issue_data in enumerate(tree_items_list):        
        if "issueData" in issue_data:
            replaced = False
            for issue in project_issues:
                if int(issue_data["issueData"]["issueId"]) == int(issue["id"]):
                    replaced = True
                    issue_data["issueData"] = issue
                    tree_items_list[index] = issue_data
                    break
            if not replaced:
                throw_error(f"Jira Issue with id {issue_data['issueData']['issueId']} not found in the project")

