from math import e
from api.azure_dev_ops.ado_helper import create_work_item, update_work_item
from config.config import ADO_ENV


def process_data_to_create_work_item(data, project_key, jira_ado_ids):
    """
    Create the body to create the Work Item on the Azure DevOps side.

    Args:
        data (dict): The folder/issue data retrieved from Jira DC.
        project_key (str): The key of the project.

    Returns:
        dict: The body in json-patch+json format necessary to create the folder as a Work Item
    """
    issue_type = (
        "Folder"
        if "folder" in data
        else data["issueData"]["fields"]["issuetype"]["name"]
    )
    work_item_type = (
        ADO_ENV.issue_type_map[issue_type]
        if issue_type in ADO_ENV.issue_type_map
        else issue_type
    )
    extracted_info = {
        "organization": ADO_ENV.organization,
        "project": project_key,
        "work_item_type": work_item_type,
        "body": [],
    }
    if "folder" in data:
        data = data["folderData"]
        description = data["description"] if data["description"] is not None else ""
        extracted_info["body"].append(
            {
                "op": "add",
                "path": "/fields/System.Description",
                "from": None,
                "value": description,
            }
        )
        extracted_info["body"].append(
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": data["name"],
            }
        )
        return extracted_info
    else:
        data = data["issueData"]
        description = (
            data["fields"]["description"]
            if data["fields"]["description"] is not None
            else ""
        )
        extracted_info["body"].append(
            {
                "op": "add",
                "path": "/fields/System.Description",
                "from": None,
                "value": description,
            }
        )
        extracted_info["body"].append(
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": data["fields"]["summary"],
            }
        )

        """The state value is mapped to the Azure DevOps state value, if the state value is not in the map, it will be used as is"""
        state_value = data["fields"]["status"]["name"]

        # Check if there is an specific mapping for the status in this work item type
        if f"{work_item_type}/{state_value}" in ADO_ENV.status_map:
            state_value = ADO_ENV.status_map[f"{work_item_type}/{state_value}"]

        # If not, check if there is a general mapping for the status
        elif state_value in ADO_ENV.status_map:
            state_value = ADO_ENV.status_map[state_value]

        extracted_info["body"].append(
            {
                "op": "add",
                "path": "/fields/System.State",
                "from": None,
                "value": state_value,
            }
        )

        add_issue_links_to_work_item(data, extracted_info, jira_ado_ids)

        return extracted_info


def add_issue_links_to_work_item(data, extracted_info, jira_ado_ids):
    """
    Add the issue links to the work item body.

    Args:
        data (dict): The issue data retrieved from Jira DC.
        extracted_info (dict): The body in json-patch+json format necessary to create the folder as a Work Item
        jira_ado_ids (dict): The ids of the issues already created on Azure DevOps.
    """
    if "issuelinks" in data["fields"]:
        for link in data["fields"]["issuelinks"]:
            link_key = 'inwardIssue' if 'inwardIssue' in link else 'outwardIssue'
            if link_key in link:
                target_issue_id = link[link_key]["id"]
                if target_issue_id not in jira_ado_ids:
                    continue
                target_workitem_id = jira_ado_ids[target_issue_id]
                if target_workitem_id:
                    link_name = link["type"]["outward"]
                    if link_name not in ADO_ENV.link_type_map:
                        raise Exception(
                            f"Link type {link_name} not found in the link map"
                        )
                    ado_link_name = ADO_ENV.link_type_map[link_name]
                    extracted_info["body"].append(
                        {
                            "op": "add",
                            "path": "/relations/-",
                            "from": None,
                            "value": {
                                "rel": ado_link_name,
                                "url": f"https://dev.azure.com/{ADO_ENV.organization}/{extracted_info['project']}/_apis/wit/workitems/{target_workitem_id}",
                            },
                        }
                    )


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
            work_item = process_data_to_create_work_item(
                issue, project_key, jira_ado_ids
            )

            state_value = None
            # Check if the state value is in the map. if yes, save it for later
            if (
                len(work_item["body"]) > 2
                and "/fields/System.State" in work_item["body"][2]["path"]
            ):
                state_value = work_item["body"][2]["value"]
                # Remove the state value from the body
                work_item["body"].pop(2)

            new_workitem = create_work_item(
                work_item["organization"],
                work_item["project"],
                work_item["work_item_type"],
                work_item["body"],
            )
            issue["id"] = new_workitem["id"]

            # If the state value was saved, add it to the work item
            if state_value and new_workitem["fields"]["System.State"] != state_value:
                body = [
                    {
                        "op": "add",
                        "path": "/fields/System.State",
                        "from": new_workitem["fields"]["System.State"],
                        "value": state_value,
                    }
                ]
                update_work_item(
                    work_item["organization"],
                    work_item["project"],
                    new_workitem["id"],
                    body,
                )

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
                raise Exception(
                    f"Jira Issue with id {issue_data['issueData']['issueId']} not found in the project"
                )
