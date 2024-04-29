from config.config import ADO_ENV
from api.azure_dev_ops.ado_helper import get_project_by_id_or_name
from api.azure_dev_ops.ease_requirements_helper import get_all_tree_items, delete_single_tree_item


def delete_tree_items_by_project_key(project_key):
    """
    Delete all tree items for a project.

    Args:
        project_key (str): The key of the project.

    Returns:
        None
    """
    project_id = get_project_by_id_or_name(ADO_ENV.organization, project_key)["id"]
    tree_items = get_all_tree_items(project_id)
    for item in tree_items:
        delete_single_tree_item(project_id, item["id"])
