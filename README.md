# Migrating an R4J Tree from Data Center to easeRequirements for Azure DevOps
This repository exemplifies how to migrate the R4J tree structure from a Jira Server or Data Center instance to easeRequirements for Azure DevOps using Python and the REST APIs. The script will create all the work items and copy the tree structure.

## Table of Contents
  - [Pre-requisites](#pre-requisites)
  - [Set up the development machine](#set-up-the-development-machine)
  - [Preparing to run the migration script](#preparing-to-run-the-migration-script)
  - [How to run the migration script](#how-to-run-the-migration-script)
    - [Optional: Clean up the tree](#optional-clean-up-the-tree)
    - [Migrate a Server or Data Center R4J tree to easeRequirements](#migrate-a-server-or-data-center-r4j-tree-to-easerequirements)
- [Known Issues and Possible Improvements](#known-issues-and-possible-improvements)
- [Disclaimer](#disclaimer)

## Pre-requisites
* A Jira Server or Data Center instance with R4J installed
* An Azure DevOps organization with easeRequirements installed
* A Jira project with R4J activated on the Jira Server or Data Center instance
* An Azure DevOps project with a selected folder work item type (see [Getting started](https://easesolutions.atlassian.net/wiki/spaces/easeRequirements/pages/2381283731/Getting+started))
* Both the Jira and the Azure DevOps projects must have the same name

## Set up the development machine
1. Install Python 3.8.9 or greater [Python official documentation](https://www.python.org/downloads/release/python-389/)
2. Clone the repository. [How to clone a repository](https://support.atlassian.com/bitbucket-cloud/docs/clone-a-repository/)
3. Install the Python dependencies 
```
    pip install -r requirements.txt
```

## Preparing to run the migration script
The script relies on a set of parameters to run. Before running the script, you need to set these up in the *config.yaml* file. An example file only is committed to this repository.

The *config.yaml* file should be similar to the example below:

```yaml
settings:
  ado_env:
    # Azure DevOps
    organization: organization-name
    application_url: https://dev.azure.com/ # For Azure DevOps server use your internal URL
    username: ado-your-username
    ado_pat: ado-personal-access-token
    issue_type_map: { Story: "User Story" }
    status_map: { "In Progress":	Active, Accepted: Resolved, Reopened: Active }

  data_center_env:
    # Data Center
    application_url: https://www.mywebsite.com/jira/
    username: data-center-username
    password: data-center-password
        # pat: data-center-personal-access-token
```    


### Azure DevOps instance configurations
  * **organization**: Name of the Organization where you have the target project.
  * **application_url**: URL of your Azure DevOps instance.
  * **username**: Azure DevOps user with WRITE rights to the project being migrated.
  * **ado_pat**: Azure DevOps Api Token to access the ADO instance. The token must have read and write rights to work items and extension data and read access to projects
  * **issue_type_map**: A map between issue type names and work item type names where the key is the Jira issue type and the value the Azure DevOps work item type
  * **status_map**: A map between Jira status and Azure DevOps states where the key is the Jira status and the value the Azure DevOps state

### Jira Server/Data Center configurations
  * **application_url**: URL to the Jira Server or Data Center instance.
  * **username**: User with READ access to the projects you want to migrate.
  * **password**: Password for the user.
  * **pat**: Alternatively to providing the username and password, you can provide a [Personal Access Token (PAT)](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

## How to run the migration script
### Optional: Clean up the tree

The script assumes that the easeRequirements project tree is empty in the ADO instance. If this is not the case, you can run the below command to empty it. It won't delete any Azure work item, but simply empty the tree.
**WARNING**: If you run the below command, the project tree will be empty. This cannot be reversed.

```
python r4ado_clean_tree.py {project_name}
```
Where *project_name* is the name of the Azure DevOps project you want to clean up. If the project name has spaces you should enclose it with single quotes on Linux or double quotes on Windows.

### Migrate a Server or Data Center R4J tree to easeRequirements

To finally migrate a tree to the Azure DevOps, just run the following script:
```
python migrate.py {project_name} {dry_run: optional}
```
Setting *dry_run* to *True* allows you to verify if the migration is possible without actually creating any items in the Azure DevOps instance. After running it on dry run mode, an HTML file will open in your default browser showing the expected tree. Example:
```
python migrate.py {project_name} True
```
If you don't specify the *dry_run* command-line parameter, it assumes to be false.

# Known Issues and Possible Improvements
* The script doesn't migrate folder attachments.
* The Script for only copies the summary, description and state to the new work item in Azure DevOps.
* The script doesn't check for user rights before running, nor existence of the right work item types or states. If the users associated with the tokens cannot perform the needed operations, the script will fail, leaving a potentially incomplete easeRequirements Tree in Azure DevOps.

# Disclaimer

THIS REPOSITORY IS PROVIDED BY THE CONTRIBUTORS “AS IS”. IT IS NOT AN OFFICIAL MIGRATION PROCEDURE SUPPORTED BY EASE SOLUTIONS OR ITS AFFILIATES. ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.