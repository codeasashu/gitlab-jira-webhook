from flask import Flask, jsonify, abort
from .webhooks.jira import jira as jirahook
from .webhooks.gitlab import gitlab as gitlabhook
from config import Config

app = Flask(__name__)
app.register_blueprint(jirahook, url_prefix='/jira')
app.register_blueprint(gitlabhook, url_prefix='/gitlab')

@app.errorhandler(403)
def custom403(error):
    return jsonify({'message': error.description}), 403