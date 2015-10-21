#!/bin/bash

export GITHUB_OAUTH_TOKEN=""
export REPOS=$(cat <<'heredoc'
---
-
  group: eddgrant
  description: PRs on Edd's Projects
  watches:
    -
      owner: eddgrant
      repo: vagrant-roller
    -
      owner: eddgrant
      repo: github-pull-request-dashboard
-
  group: fbd
  watches:
    -
      owner: bbc
      repo: eng-pcs-squirrel
heredoc)

echo "GitHub OAUTH Token: ${GITHUB_OAUTH_TOKEN}"
echo "REPOS: ${REPOS}"
echo "Starting Pull Requests App"
${VENV_DIR}/bin/gunicorn --config=gunicorn.py pull_requests.pull_requests_web:app --debug --access-logfile - --error-log - --log-config logging.conf