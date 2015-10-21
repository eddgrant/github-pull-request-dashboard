import logging
from datetime import datetime

import requests
import os
from flask import Flask, render_template
import yaml


app = Flask(__name__)

default_repos = """
---
-
  group: amp
  description: AMP Pull Requests
  watches:
    -
      owner: bbc
      repo: pcs-cloudtools
    -
      owner: bbc
      repo: pcs-snitch
    -
      owner: bbc
      repo: eng-pcs-hello-world
    -
      owner: bbc
      repo: eng-pcs-ansible
    -
      owner: bbc
      repo: pcs-shared-resources
    -
      owner: bbc
      repo: eng-pcs-turncoat
    -
      owner: bbc
      repo: pcs-sns-to-slack
    -
      owner: bbc
      repo: pcs-lambda-deployer
    -
      owner: bbc
      repo: pcs-snitch-deployer
    -
      owner: bbc
      repo: eng-pcs-leech
    -
      owner: bbc
      repo: eng-pcs-fabric-mock
    -
      owner: bbc
      repo: eng-pcs-squirrel
    -
      owner: bbc
      repo: eng-pcs-sloth
    -
      owner: bbc
      repo: eng-pcs-sloth-deployer
    -
      owner: bbc
      repo: eng-pcs-em3-mysql-database
    -
      owner: bbc
      repo: pcs-amp-end-to-end-tests
    -
      owner: bbc
      repo: eng-pcs-em3-db2-to-mysql-exporter
-
  group: fbd
  watches:
    -
      owner: bbc
      repo: eng-pcs-squirrel
"""


def load_app_config():
    app.config.from_object(__name__)

    github_oauth_token = os.environ.get("GITHUB_OAUTH_TOKEN", None)
    app.config["GITHUB_OAUTH_TOKEN"] = github_oauth_token

    repos_string = os.environ.get("REPOS", default_repos)
    repos = yaml.load(repos_string)
    app.config["REPOS"] = repos

    github_api_base_url = os.environ.get("GITHUB_API_BASE_URL", "https://api.github.com/repos")
    app.config["GITHUB_API_BASE_URL"] = github_api_base_url

    LOGGER.debug("App config loaded successfully: {}".format(app.config))


def configure_logging():
    global LOGGER
    LOGGER = logging.getLogger("pull_requests")


def get_requests(repo_watches):
    unassigned = []
    assigned = []

    for watch_item in repo_watches:
        github_api_base_url = app.config.get("GITHUB_API_BASE_URL")
        url = "{github_api_base_url}/{owner}/{repo}/pulls".format(github_api_base_url=github_api_base_url, owner=watch_item['owner'], repo=watch_item['repo'])
        headers = {'Authorization': "token {}".format(app.config.get("GITHUB_OAUTH_TOKEN"))}
        r = requests.get(url, headers=headers, stream=True)
        pull_request_count = len(r.json())

        if pull_request_count > 0:

            for pull_request_index in range(0, pull_request_count):
                current_pull_request = r.json()[pull_request_index]
                avatar = str(current_pull_request['user']['avatar_url'])
                user = str(current_pull_request['user']['login'])
                num = str(current_pull_request['number'])
                assignee = str(current_pull_request['assignee'])
                date_posted = datetime.strptime(current_pull_request['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                # Calculating number of hours since pull request was pushed at by subtracting it from datetime.now()
                now = datetime.utcnow()
                # Dividing by 3600 is equivalent to dividing by 60 (secs in a min) and then 60 (mins in an hour) again
                # Cast in a float to more effectively work out how long ago a pull request was pushed in the template
                waited = abs((now - date_posted).seconds/float(3600))
                html_url = str(current_pull_request['html_url'])

                if assignee == "None":
                    unassigned.append({'repo': watch_item,
                                       'num': num,
                                       'date_posted': date_posted,
                                       'user': user,
                                       'avatar': avatar,
                                       'waited': waited,
                                       'html_url': html_url})
                else:
                    assignee = str(current_pull_request['assignee']['login'])
                    assigned.append({'repo': watch_item,
                                     'num': num,
                                     'date_posted': date_posted,
                                     'user': user,
                                     'avatar': avatar,
                                     'waited': waited,
                                     'assignee': assignee,
                                     'html_url': html_url})

        else:

            continue

        r.close()

    return [unassigned, assigned]

configure_logging()
load_app_config()


@app.errorhandler(404)
def not_found(error):
    header = 'Not Found - '
    groups = [group_config['group'] for group_config in app.config.get('REPOS')]
    return render_template('404.html', header=header, teams=groups), 404


@app.route('/')
def main():
    groups = [group_config['group'] for group_config in app.config.get('REPOS')]
    return render_template('index.html', groups=groups)


# TODO: What about a root group which responds to '/'?
@app.route('/pulls/<string:group>')
def show_pull_requests(group):
    for this_group_config in app.config['REPOS']:
        if this_group_config['group'] == group:
            group_config = this_group_config
    # TODO: If there's no group_config - redirect to the 404 page with a nice message explaining what has happened.
    description = group_config.get('description', 'Open Pull Requests')
    pr_list = get_requests(group_config['watches'])
    return render_template('pull-requests.html', pr_list=pr_list, description=description)


@app.route('/ping/ping')
def healthcheck():
    return "", 200

# Called only when running under Flask.
if __name__ == '__main__':
    app.run(debug=True)
