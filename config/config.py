import yaml
from pathlib import Path

YML_ENV = Path(__file__).parents[1] / 'config.yaml'


def read_yaml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class AdoSettings:

    def __init__(self, env_yml_file):
        env_obj = read_yaml_file(env_yml_file)
        env_settings = env_obj['settings']['ado_env']
        self.organization = env_settings['organization']
        self.application_url = env_settings['application_url']
        self.username = env_settings['username']
        self.ado_pat = env_settings['ado_pat']
        self.issue_type_map = env_settings['issue_type_map'] if 'issue_type_map' in env_settings else {}
        self.status_map = env_settings['status_map'] if 'status_map' in env_settings else {}


class DataCenterSettings:

    def __init__(self, env_yml_file):
        env_obj = read_yaml_file(env_yml_file)
        env_settings = env_obj['settings']['data_center_env']
        self.application_url = env_settings['application_url']
        if 'pat' in env_settings and env_settings['pat'] != '' and env_settings['pat'] is not None:
            self.pat = env_settings['pat']
        else:
            self.username = env_settings['username']
            self.password = env_settings['password']
            self.pat = ''


ADO_ENV = AdoSettings(env_yml_file=YML_ENV)
DC_ENV = DataCenterSettings(env_yml_file=YML_ENV)
