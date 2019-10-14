from flask import Blueprint, abort
from ..gitlab import MergeRequest
from ..jira import JiraApi
from ..decorators import filter_webhook
from config import Config

gitlab = Blueprint('gitlab', __name__)

@gitlab.route('/webhook/merge_request', methods=['POST'])
@filter_webhook(MergeRequest.object_kind.MERGE_REQUEST)
def merge_event_hook(webhook_data):
    gl = MergeRequest(webhook_data)
    jira_api = JiraApi().get_instance()

    source_branch = gl.get_source_branch()
    target_branch = gl.get_target_branch()
    project_link = gl.get_source_repo()
    commit_hash_link = gl.get_commit_hash_link()
    is_wip = gl.is_wip()
    issues = []

    if is_wip:
        return abort(403, 'Work in progress')

    # if MR stage -> master
    if source_branch == Config.GITLAB_STAGE_BRANCH and target_branch == 'master':
        # Search all JIRA issues "under review" having this gitlab link
        issues = jira_api.search_issues(
            f"status = '{Config.JIRA_INREVIEW_STAGE}' AND gitlab='{project_link}'"
        )
        comment = f'Closed in {commit_hash_link}'
    # if MR somebranch -> stage
    elif target_branch == Config.GITLAB_STAGE_BRANCH:
        source_branch = 'JIRA-HEL-20'
        jira_issue_key = gl.jiraify_branch_name(source_branch)
        if not jira_issue_key:
            return abort(403, f'Invalid issue key or target branch {target_branch}')
        issue = jira_api.issue(jira_issue_key)
        issues.append(issue)
        comment = f'Fixed in {commit_hash_link}'

    transition_id = Config.JIRA_TRANSITIONS.get(target_branch)
    if int(transition_id) > 0 and len(issues) > 0:
        for issue in issues:
            jira_api.transition_issue(issue, transition_id, comment=comment)

    json_data = gl.get_json()
    return json_data