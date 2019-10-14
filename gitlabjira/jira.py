import json
from config import Config
import re
from jira import JIRA as JiraLib

CUSTOM_FIELD_REGEX = r"^customfield_.+"
GITLAB_PROJECT_REGEX = r"^(https?\:\/\/|git\@)?(gitlab\.com[\/|\:])(.*)"

class Jira(object):
    def __init__(self, issue_key, webhook_data):
        self.issue_key = issue_key
        if isinstance(webhook_data, str):
            webhook_data = json.loads(webhook_data)
        self.webhook_data = webhook_data

    def get_fields(self):
        return self.webhook_data['issue']['fields']
    
    def get_summary(self):
        return self.webhook_data['issue']['fields']['summary'] or f'ISSUE {self.issue_key}'
    
    def get_description(self):
        fields = self.get_fields()
        for fieldname, val in fields.items():
            if fieldname == 'description':
                return val
        return ''
    
    def get_gitlab_link(self):
        fields = self.get_fields()
        if isinstance(fields, dict):
            for fieldname, val in fields.items():
                if re.findall(CUSTOM_FIELD_REGEX, fieldname) and isinstance(val, str):
                    gitlab_repo = None
                    matches = re.search(GITLAB_PROJECT_REGEX, val)
                    if matches:
                        try:
                            gitlab_repo = matches.group(3)
                        except AttributeError as e:
                            continue
                    if gitlab_repo:
                        # Strip out .git from name if any
                        return gitlab_repo.rstrip('.git')
        return None
    
    def gitlabify_branch_name(self):
        return f"{Config.GITLAB_BRANCH_KEYPREFIX}{self.issue_key.lstrip(Config.GITLAB_BRANCH_KEYPREFIX)}"


class JiraApi(object):
    def __init__(self, site_name = Config.JIRA_SITE, username=Config.JIRA_USERNAME, token=Config.JIRA_TOKEN):
        self.jira_instance = JiraLib(site_name, basic_auth=(username, token))
        print(self.jira_instance)
    
    def get_instance(self):
        return self.jira_instance