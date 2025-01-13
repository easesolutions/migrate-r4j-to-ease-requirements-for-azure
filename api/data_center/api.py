import requests
from uplink import Consumer, get
from uplink.auth import BasicAuth, BearerToken
import urllib3
from urllib3 import exceptions
from config.config import DC_ENV


class R4jApi(Consumer):
    """
    Represents a Requirements Management for Jira Data Center API client.

    This class provides the method to interact with the Requirements Management
    for Jira Data Center API and perform operation of retrieve Tree structure.
    """
    ease_endpoint_01 = 'rest/com.easesolutions.jira.plugins.requirements/1.0/'

    @get("{}{}".format(ease_endpoint_01, 'tree/{project_key}'))
    def get_complete_tree_structure_by_project_key(self, project_key):
        """Get the folder structure of the project key provided"""


class JiraAPI(Consumer):
    """
    Represents a Jira Data Center API client.

    This class provides methods to interact with the Jira Data Center API
    and perform operations such as retrieving projects and issues.
    """
    jira_endpoint = 'rest/api/2/'

    @get("{}{}".format(jira_endpoint, 'issue/{issue_key}'))
    def get_issue_by_key(self, issue_key):
        """Get issue details by key"""

    @get("{}{}".format(jira_endpoint, 'project'))
    def get_all_projects(self):
        """Get all projects"""
    
    @get("{}{}".format(jira_endpoint, 'project/{project_id_or_key}'))
    def get_project_by_id_or_key(self, project_id_or_key):
        """Get project details by project id or key"""

    @get("{}{}".format(jira_endpoint, 'search?jql=project={project_key} OR issue in requirementsPath("{project_name}")&maxResults=1000'))
    def get_all_issues_in_project_by_project_key_or_tree(self, project_key, project_name):
        """Get all issues in project by project key"""


urllib3.disable_warnings(exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False
api_auth = BasicAuth(DC_ENV.username, DC_ENV.password) if DC_ENV.pat == '' else BearerToken(DC_ENV.pat)
r4j_api = R4jApi(DC_ENV.application_url, auth=api_auth, client=session)
jira_api = JiraAPI(DC_ENV.application_url, auth=api_auth, client=session)
