ROOT_ITEM = {'issue_key': -1, 'level': 1}


def read_and_process_tree_items(data_input, _data_output, level=1, folder_id=-1, issue_id=None):
    """
    Get the tree data from Data Center and

    Args:
        data_input (dict): R4J tree retrieved from the data center instance
        _data_output: (list): List to be populated with the data processed
        level (int): Int that represents the level of the tree
        folder_id (str): id of the folder parent
        issue_id (str): id of the issue parent
    """
    root = data_input["id"]
    parent_id = folder_id if folder_id else issue_id

    for folder in data_input["folders"]:
        data_folders = {"id": folder["name"], "folders": folder["folders"], "issues": folder["issues"]}
        position = folder["absolutePosition"]
        _data_output.append({"parent": root, "folder_name": folder["name"], "position": position, "level": level,
                             "folder": True, "folderData": folder, "jira_id": folder["id"], "jira_parent_id": parent_id
                             })
        read_and_process_tree_items(data_folders, _data_output, level + 1, folder["id"])

    for issue in data_input["issues"]:
        position = issue["absolutePosition"]
        if "childReqs" in issue.keys() and len(issue["childReqs"]["childReq"]) != 0:
            data_issue = {"id": issue["key"], "folders": [], "issues": issue["childReqs"]["childReq"]}
            _data_output.append({"parent": root, "issue_key": issue["key"], "summary": issue["summary"],
                                 "position": position, "level": level, "issueData": issue, "jira_id": issue["issueId"],
                                 "jira_parent_id": parent_id})
            read_and_process_tree_items(data_issue, _data_output, level + 1, issue["issueId"])
        else:
            _data_output.append({"parent": root, "issue_key": issue["key"], "summary": issue["summary"],
                                 "position": position, "level": level, "issueData": issue, "jira_id": issue["issueId"],
                                 "jira_parent_id": parent_id})


def get_sorted_children(parent, tree_items):
    """
    Get and sort the children of a parent node in the tree.

    Args:
        parent: The parent node whose children are to be sorted.
        tree_items: The list of all tree elements.

    Returns:
        A list of sorted children.
    """
    children = [item for item in tree_items
                if item["parent"] == parent["issue_key"] and item["level"] == parent["level"]]
    return sorted(children, key=lambda x: x["position"])


def traverse_and_order_tree(children, tree_items, ordered_tree):
    """
    Recursively traverse and order the tree starting from given child nodes.

    Args:
        children: The list of children of a node to be sorted.
        tree_items: The complete list of tree elements.
        ordered_tree: The list where ordered tree elements will be stored.

    Returns:
        None
    """
    for child in children:
        ordered_tree.append(child)
        issue_key = child['issue_key'] if child.get('issue_key') else child['folder_name']

        sorted_children = get_sorted_children({"issue_key": issue_key, "level": child['level']+1}, tree_items)
        traverse_and_order_tree(sorted_children, tree_items, ordered_tree)


def sort_tree(tree_items):
    """
    Sort the hierarchical tree in deep order.

    Args:
        tree_items: The complete list of tree elements.

    Returns:
        A list of tree elements ordered in depth-first manner.
    """
    ordered_tree = []
    root_children = get_sorted_children({"issue_key": -1, "level": 1}, tree_items)
    traverse_and_order_tree(root_children, tree_items, ordered_tree)
    return ordered_tree
