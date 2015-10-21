#!/bin/bash

export GITHUB_OAUTH_TOKEN="put your github oauth token here"
export REPOS=$(cat <<'heredoc'
---
-
  group: edd
  description: PRs on Edd's Projects
  watches:
    -
      owner: eddgrant
      repo: vagrant-roller
    -
      owner: eddgrant
      repo: github-pull-request-dashboard
    -
      owner: basejump
      repo: markdown-plus
-
  group: beeb
  watches:
    -
      owner: bbc
      repo: gatling-load-tests
    -
      owner: bbc
      repo: hive-runner
-
  group: hmrc
  watches:
    -
      owner: hmrc
      repo: ct-calculations
heredoc)

echo "GitHub OAUTH Token: ${GITHUB_OAUTH_TOKEN}"
echo "REPOS: ${REPOS}"
echo "Starting Pull Requests App"
~/.pyenv/versions/venv-github-pull-requests-dashboard-2.7.10/bin/gunicorn --config=gunicorn.py pull_requests.pull_requests_web:app --debug --access-logfile - --error-log - --log-config logging.conf