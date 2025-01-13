"""Implements the migration from an R4J project to easeRequirements for Azure DevOps"""
from api import r4j_helper
from api.azure_dev_ops import ado_helper, ease_requirements_helper
from api.data_center.jira_helper import get_all_issues_in_project_by_project_key_or_tree, get_project_by_name
from config.config import ADO_ENV
from report.log_and_report import (generate_expected_tree_html,
                                   initialize_logging, open_report_html,
                                   write_logging_simple_message)
from utilities import ado_verifications, read_and_process_tree_items
from utilities.migrate_tree import (
    create_work_items_on_ado, replace_tree_issues_data_with_jira_issue_data)
from utilities.transform_data import sort_tree

LOG_FILE = "migration"


def run_migration(project_name, dry_run):
    """
    Runs the migration process for transferring thr requirements tree from Jira DC to Azure DevOps.

    Args:
        project_name (str): The name of the project in the Azure DevOps side and the project key on the Jira DC side.
        dry_run (bool): If True, performs a dry run without making any changes.

    Returns:
        None
    """
    initialize_logging(LOG_FILE)

    # Azure DevOps verifications
    write_logging_simple_message("Azure DevOps verifications started")
    flag_ado_verifications = ado_verifications.run_project_ado_verifications(
        ADO_ENV.organization, project_name)
    if flag_ado_verifications:
        write_logging_simple_message("All verifications successfully")
    else:
        write_logging_simple_message(
            "Azure DevOps verifications failed. Exiting...")
        return

    # Download the Issue from Jira DC
    write_logging_simple_message("Download the issues from Jira DC")
    project = get_project_by_name(project_name)
    project_key = project["key"]
    project_issues = get_all_issues_in_project_by_project_key_or_tree(project_key, project_name)[
        "issues"]

    # Download the tree from R4JDC
    write_logging_simple_message("Download the tree from R4JDC")
    data_center_tree = r4j_helper.get_complete_tree_structure_by_project_key(
        project_key)
    tree_items_list = []
    read_and_process_tree_items(data_center_tree, tree_items_list)

    # Replace r4j the issues data with Jira data center Issue data
    write_logging_simple_message("Updating issue data")
    replace_tree_issues_data_with_jira_issue_data(
        tree_items_list, project_issues)

    # Check if all issues are found on the Jira Cloud instance
    write_logging_simple_message(
        "Check if all issues are found on the Azure DevOps instance")
    jira_ado_ids = {"-1": -1}
    verify_issues_in_ado = ado_verifications.verify_all_data_center_tree_issues_in_ado_instance(jira_ado_ids,
                                                                                                tree_items_list,
                                                                                                ADO_ENV.organization,
                                                                                                project_name)
    if verify_issues_in_ado:
        write_logging_simple_message(
            "ADO ISSUES: Tree data center issues are found on the ADO instance.")
    else:
        write_logging_simple_message(
            f"{len(jira_ado_ids) -1} data center issues found on the ADO, "
            f"going to create {len(tree_items_list) - (len(jira_ado_ids) -1)} WorkItems")

        # Get folder type
        write_logging_simple_message("Get folder work item type")
        folder_type, _ = ease_requirements_helper.get_folder_work_item_type(
            ADO_ENV.organization, project_name)

        # Create all the issues as Work Items
        write_logging_simple_message("Creating issues as Work Items")
        create_work_items_on_ado(
            tree_items_list, jira_ado_ids, folder_type, project_name)

    if not dry_run:
        # Replace the Jira id with the Ado ids
        write_logging_simple_message(
            "Replacing Jira Ids with the Work Item Ado Ids")
        for index, issue in enumerate(tree_items_list):
            issue["parent_id"] = jira_ado_ids[str(issue["jira_parent_id"])]
            tree_items_list[index] = issue

        # Sort the tree item list by level and position
        write_logging_simple_message("Sort tree to create")
        deep_order_tree = sort_tree(tree_items_list)

        # Create the new tree on Azure DevOps
        write_logging_simple_message("Creating the new tree on Azure DevOps")
        tree_items_created = []
        project_id = ado_helper.get_project_by_id_or_name(
            ADO_ENV.organization, project_name)["id"]
        for issue in deep_order_tree:
            tree_items_created.append(ease_requirements_helper.create_single_tree_item(project_id, issue["id"],
                                                                                       issue["parent_id"]))
        write_logging_simple_message("Migration completed")
        write_logging_simple_message(
            "Created " + str(len(tree_items_created)) + " items in the easeRequirements tree")

    # Generate report HTML with expected tree structure
    else:
        deep_order_tree = sort_tree(tree_items_list)
        write_logging_simple_message("Expected tree HTML generating")
        expected_tree_path = "./report/expected_tree.html"
        generate_expected_tree_html(
            expected_tree_path, deep_order_tree, project_name)
        open_report_html(expected_tree_path)
