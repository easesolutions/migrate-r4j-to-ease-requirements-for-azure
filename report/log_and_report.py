import logging
import webbrowser
import os

UL_OPEM = "<ul>"
UL_CLOSE = "</ul>"
LI_OPEN = "<li>"
LI_CLOSE = "</li>"
OPEN_ROOT = '<a id="root" class="label">'
OPEN_A = '<a class="label"><icon></icon><span class="issue fa-check-square"></span>'
OPEN_A_FOLDER = '<a class="label"><icon></icon><span class="folder fa-folder"></span>'
CLOSE_A = '</a>'
FONT_AWESOME = '<link rel="stylesheet" href="' \
               'https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">'
STYLESHEET = '<link rel="stylesheet" href="style.css">'
SCRIPT = '<script src="main.js"></script>'
HEAD = '<head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" ' \
       'content="width=device-width, initial-scale=1.0"><title>Expected Tree</title></head>'
HEADER = '<header><h1>R4J Data Center Migration to Azure DevOps</h1><h2>Expected tree</h2></header>'
NOTE = ''


def initialize_logging(file_name):
    """
        Initialize the logging file to save the log of the script.

        Args:
            file_name (str): Name of the log file.

        Returns:
            None
        """
    logging.basicConfig(format='%(asctime)s: %(levelname)s => %(message)s', filename=f'./report/{file_name}.log',
                        level=logging.DEBUG)


def write_logging_server_response(response, message, error=False, type_error=None):
    """
    Write log with a server response.

    Args:
        response (response): Response of the server.
        message (str): Log message.
        error (bool): Specify if occurred error in the server response.
        type_error (error): The type of the error.

    Returns:
        None
    """
    path_url = response.request.path_url
    jwt_string = '?jwt' if '?jwt' in path_url else '&jwt'
    if jwt_string in path_url:
        method_status_endpoint = f"\t\t{response.request.method} {path_url[:path_url.index(jwt_string)]} " \
                             f"=> Status code: {response.status_code}"
    else:
        method_status_endpoint = f"\t\t{response.request.method} {path_url} => Status code: {response.status_code}"
    response_content = f"\t\tResponse content: {response.json()}" \
        if response.status_code < 400 else f"\t\t{response.content}"
    if not error:
        print(f"\t{message}")
        logging.info(f"\t{message}")
        logging.info(method_status_endpoint)
        if response.request.method == "POST":
            logging.info(f"\t\tRequest body: {response.request.body}")
        logging.info(response_content)
    else:
        logging.error(f"\t{message}")
        logging.error(method_status_endpoint)
        logging.error(response_content)
        raise_an_error(message, type_error)


def write_logging_dry_run_message(message, request_body):
    """
    Write log with a dry run message.

    Args:
        message (str): Log message
        request_body (str): Example request body

    Returns:
        None
    """
    print(f"\t{message}")
    logging.info(f"\t{message}")
    logging.info(f"\t\tRequest body: {request_body}")


def write_logging_simple_message(message):
    """
    Write log with a simple message.

    Args:
        message (str): Log message

    Returns:
        None
    """
    print(message)
    logging.info(message)


def write_logging_error(message):
    """
    Write log with an error message.

    Args:
        message (str): Log error message

    Returns:
        None
    """
    print(f"ERROR: {message}")
    logging.error(message)    


def create_item_on_current_level(data, a_label):
    """
    Create html item based on current level

    Args:
        data (dict): Item data
        a_label (str): Specify if it is a Folder or an Issue/WorkItem

    Returns:
        report_html (str): Html with the item
    """
    issue_title = data['summary'] if data.get('issue_key') else data['folder_name']
    report_html = f"{LI_CLOSE}{LI_OPEN}{a_label} {issue_title}{CLOSE_A}"
    return report_html


def create_item_on_next_level(data, a_label):
    """
    Create html item based on next level

    Args:
        data (dict): Item data
        a_label (str): Specify if it is a Folder or an Issue/WorkItem

    Returns:
        report_html (str): Html with the item
    """
    issue_title = data['summary'] if data.get('issue_key') else data['folder_name']
    report_html = f"{UL_OPEM}{LI_OPEN}{a_label} {issue_title}{CLOSE_A}"
    return report_html


def create_item_on_previous_level(data, a_label, level_difference):
    """
    Create html item based on previous level

    Args:
        data (dict): Item data
        a_label (str): Specify if it is a Folder or an Issue/WorkItem
        level_difference (int): Level difference

    Returns:
        report_html (str): Html with the item
    """
    issue_title = data['summary'] if data.get('issue_key') else data['folder_name']
    close_level = f"{LI_CLOSE}{UL_CLOSE}" * level_difference
    report_html = f"{close_level}{LI_OPEN}{a_label}  {issue_title}{CLOSE_A}"
    return report_html


def generate_expected_tree_html(path, issue_process_list, project_key):
    """
    Generate report HTML with the expected easeRequirements tree

    Args:
        path (str): Path to generate the expected tree html.
        issue_process_list (list): List with all jira issues and Azure DevOps work items.
        project_key (str): The jey of the project

    Returns:
        None
    """
    report_html = f"<html><body>{HEAD}{HEADER}{NOTE}{UL_OPEM}{LI_OPEN}{OPEN_ROOT}{project_key}{CLOSE_A}"
    current_level = 0
    final_level = 0
    for data in issue_process_list:
        a_label = OPEN_A_FOLDER if "folder" in data.keys() else OPEN_A
        if data["level"] == current_level:
            report_html += create_item_on_current_level(data, a_label)
        if data['level'] > current_level:
            report_html += create_item_on_next_level(data, a_label)
        if data['level'] < current_level:
            level_difference = (current_level - data['level'])
            report_html += create_item_on_previous_level(data, a_label, level_difference)
        current_level = data["level"]
        final_level = current_level

    repeat = final_level + 1
    report_html += f"{LI_CLOSE}{UL_CLOSE}" * repeat

    html = report_html + f"{SCRIPT}{STYLESHEET}{FONT_AWESOME}</body></html>"

    hs = open(path, 'w')
    hs.write(html)


def open_report_html(path):
    """
    Open the report html in a web browser.

    Args:
        path (str): Path to generate the expected tree html.

    Returns:
        None
    """
    abs_path = os.path.abspath(path)
    webbrowser.open(abs_path)


def raise_an_error(message, type_error):
    """
    Raise an error with a  message.

    Args:
        message (str): Log error message
        type_error (error): The type of the error.

    Returns:
        None
    """
    try:
        raise type_error(message)
    except type_error as err:
        print(f"\n{err}")
        print(type(err))
        raise SystemExit()
