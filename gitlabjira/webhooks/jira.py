from flask import Blueprint, request
import json
from ..gitlab import Gitlab as MyOpGitlab
from ..jira import Jira as MyOpJira
from config import Config

jira = Blueprint('jira', __name__)

@jira.route('/webhook')
def hook():
    issue_key = request.args.get('issuekey', None)
    issuebody = request.get_json(silent=True)
    gitlab_repo = None

    if issue_key:
        jira = MyOpJira(issue_key, issuebody)
        issue_summary = jira.get_summary()
        issue_description = jira.get_description()
        gitlab_repo = jira.get_gitlab_link()
        issue_branch_name = jira.gitlabify_branch_name()

    if gitlab_repo:
        gl = MyOpGitlab(gitlab_repo)
        source_branch = gl.get_branch(issue_branch_name)
        target_branch = gl.get_branch(Config.GITLAB_STAGE_BRANCH)
        title = f'WIP: {issue_summary}'
        description = f'Links {issue_key} {issue_description}'
        gl.create_mr(source_branch, target_branch, title, description)

    response = dict(issuekey=issue_key, issuebody=issuebody)
    return json.dumps(response)