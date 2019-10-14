import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    # App specific configs
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', '3000')
    DEBUG = os.getenv('APP_ENV', 'prod') == 'dev'

    # Gitlab specific configs
    GITLAB_SERVER = os.getenv('GITLAB_SERVER', 'https://gitlab.com')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    GITLAB_BRANCH_KEYPREFIX = 'JIRA-'
    GITLAB_STAGE_BRANCH = 'stage'

    # Jira specific configs
    JIRA_USERNAME = os.getenv('JIRA_USERNAME')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    JIRA_SITE = os.getenv('JIRA_SITE')
    JIRA_TRANSITIONS = {
        'stage': os.getenv('TRANSITION_STAGE', 0),
        'master': os.getenv('TRANSITION_MASTER', 0)
    }
    JIRA_INREVIEW_STAGE = 'Backlog'
