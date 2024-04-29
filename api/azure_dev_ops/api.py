"""Implements the easeRequirements and Azure DevOps APIs"""
import requests
from uplink import Consumer, get, post, headers, json, Body, put, delete
from uplink.auth import BasicAuth
import urllib3
from urllib3 import exceptions
from config.config import ADO_ENV


class EaseRequirementsForAzureDevopsApi(Consumer):
    """
    A class representing the easeRequirements for Azure DevOps API.

    This class provides methods to interact with easeRequirements using 
    the Azure DevOps API for managing tree items and folder work item types.
    """
    API_VERSION = "3.2-preview"
    url_tree_items = f"{ADO_ENV.organization}/_apis/ExtensionManagement/InstalledExtensions/easesol/" \
                     "ease-requirements/Data/Scopes/Default/Current/Collections/TreeItems_"
    url_folder_work_item_type = f"{ADO_ENV.organization}/_apis/ExtensionManagement/InstalledExtensions/easesol/" \
                                "ease-requirements/Data/Scopes/Default/Current/Collections/" \
                                "%24settings/Documents/Settings_"

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @headers({"Content-Type": "application/json"})
    @json
    @put("{}{}".format(url_tree_items, "{project_id}/Documents/"))
    def create_single_tree_item(self, project_id, body: Body):
        """Create a single tree item"""

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{}{}".format(url_tree_items, "{project_id}/Documents/"))
    def get_all_tree_items(self, project_id):
        """Get all the tree items"""

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @delete("{}{}".format(url_tree_items, "{project_id}/Documents/{item_id}"))
    def delete_single_tree_item(self, project_id, item_id):
        """Delete item from the tree by id"""

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{}{}".format(url_folder_work_item_type, "{project_id}"))
    def get_folder_work_item_type(self, project_id):
        """Get the folder work item type"""


class AzureDevOpsApi(Consumer):
    """
    Represents an Azure DevOps API client.

    This class provides methods to interact with the Azure DevOps API
    and perform operations such as retrieving projects, work items, and
    creating new work items.

    Attributes:
        API_VERSION (str): The API version to be used for API requests.
        API_VERSION_WIQL (str): The API version to be used for WIQL queries.
    """

    API_VERSION = "7.1-preview.3"
    API_VERSION_WIQL = "5.1"

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{organization}/_apis/projects")
    def get_all_projects_by_organization(self, organization):
        """Get all projects by organization"""

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{organization}/_apis/projects/{project_id_or_name}")
    def get_project_by_id_or_name(self, organization, project_id_or_name):
        """Get project by id or name"""

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{organization}/{project}/_apis/wit/workitems/{work_item_id}")
    def get_work_item_by_id(self, organization, project, work_item_id):
        """Get work item by id"""

    @headers({"Accept": f"application/json-patch+json; api-version={API_VERSION}"})
    @headers({"Content-Type": "application/json-patch+json"})
    @json
    @post("{organization}/{project}/_apis/wit/workitems/${work_item_type}")
    def create_work_item(self, organization, project, work_item_type, body: Body):
        """Create new WorkItem"""

    @headers({"Accept": f"application/json; api-version={API_VERSION_WIQL}"})
    @headers({"Content-Type": "application/json"})
    @json
    @post("{organization}/{project}/{team}/_apis/wit/wiql?top={top}")
    def query_by_wiql(self, organization, project, team, top, body: Body):
        """Wiql - Query by Wiql, were top is the max number of results to return."""

    @headers({"Accept": f"application/json; api-version={API_VERSION_WIQL}"})
    @headers({"Content-Type": "application/json"})
    @json
    @post("{organization}/{project}/_apis/wit/workitemsbatch")
    def get_work_items_batch(self, organization, project, body: Body):
        """Get Work Items Batch"""


urllib3.disable_warnings(exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False
api_auth = BasicAuth(ADO_ENV.username, ADO_ENV.ado_pat)
ado_api = AzureDevOpsApi(ADO_ENV.application_url,
                         auth=api_auth, client=session)
ease_requirements_api_auth = BasicAuth(ADO_ENV.ado_pat, "")
ease_requirements_url = f"https://extmgmt.{ADO_ENV.application_url.split('//')[-1]}"
ease_requirements_api = EaseRequirementsForAzureDevopsApi(ease_requirements_url, auth=ease_requirements_api_auth,
                                                          client=session)
