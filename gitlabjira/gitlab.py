import gitlab
import json
import re
from config import Config

class Gitlab(object):
    def __init__(self, repo, server = Config.GITLAB_SERVER, token=Config.GITLAB_TOKEN):
        self.repo = repo
        self.server = server
        self.token = token
        self.gl = gitlab.Gitlab(server, private_token=token)
        self.gl.auth()
    
    def get_instance(self):
        return self.gl
    
    def get_project(self, repo):
        repo = repo if repo else self.repo
        if not self.project:
            self.project = self.gl.projects.get(repo)
        if not  self.project:
            raise Exception('Project does not exists')
        return self.project

    def create_branch(self, branch_name, _ref='master'):
        project = self.get_project()
        project.branches.create({'branch': branch_name,'ref': _ref})
    
    def get_branch(self, branch_name):
        project = self.get_project()
        branch = project.branches.get(branch_name)
        if not branch and (branch_name == 'stage'):
            self.create_branch(branch_name)
    
    def create_mr(self, source_branch, target_branch, title='WIP: MR', description=''):
        project = self.get_project()
        project.mergerequests.create({
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'description': description
        })
        return self.gl.projects.get(repo)
    
    def jiraify_branch_name(self, branch_name):
        if Config.GITLAB_BRANCH_KEYPREFIX in branch_name:
            return branch_name.lstrip(Config.GITLAB_BRANCH_KEYPREFIX)
        return None


class GitlabWebhook(Gitlab):
    class object_kind(object):
        PIPELINE = 'pipeline'
        MERGE_REQUEST = 'merge_request'
    
    def __init__(self, webhook_data):
        super().__init__(None)
        if isinstance(webhook_data, str):
            webhook_data = json.loads(webhook_data)
        self.data = webhook_data
    
    def get_json(self):
        return self.data
    
    def get_raw(self):
        return json.dumps(self.data)
    
    def get_source_repo(self):
        return self.data['project']['git_http_url'].rstrip('.git')
    
class MergeRequest(GitlabWebhook):
    def get_source_branch(self):
        return self.data['object_attributes']['source_branch']
    
    def get_target_branch(self):
        return self.data['object_attributes']['target_branch']

    def is_wip(self):
        return self.data['object_attributes']['work_in_progress']
    
    def get_commit_hash(self, short=True):
        commithash = self.data['object_attributes']['last_commit']['id']
        return commithash[0:8] if short else commithash
    
    def get_commit_hash_link(self):
        return self.data['object_attributes']['last_commit']['url']