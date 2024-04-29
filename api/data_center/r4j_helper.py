from api.data_center.api import r4j_api
from report.log_and_report import write_logging_server_response, write_logging_error


def get_complete_tree_structure_by_project_key(project_key):
    response = r4j_api.get_complete_tree_structure_by_project_key(project_key)
    if response.status_code == 200:
        message = "The Data Center tree structure was successfully retrieved"
        write_logging_server_response(response, message)
        return response.json()
    else:
        message = "Failed to download the Data Center tree structure"
        write_logging_error(message)
        message = "DATA CENTER RETRIEVE TREE ERROR: The Data Center tree could not be retrieved"
        write_logging_server_response(response, message, True, ConnectionError)  # CHECK ERROR
