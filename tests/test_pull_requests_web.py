import os
import yaml

os.environ["DISABLE_GITHUB_POLLING"] = "True"

default_repos_string = """
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

os.environ["REPOS"] = default_repos_string
default_repos = yaml.load(default_repos_string)
# ENV vars must be set prior to loading the pull_requests_web module

import unittest
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from mock import MagicMock
from nose.tools import assert_in, eq_
from pull_requests import pull_requests_web
import pull_requests


def check_content_type(headers, type_string):
        assert_in(type_string, headers['Content-Type'])


class PullRequestWebTest(unittest.TestCase):

    assigned = [{'repo': {'owner': 'bbc', 'repo': 'app-config-qa'},
                 'assignee': 'tomvanneerijnen',
                 'num': '99',
                 'avatar': 'https: //identicons.github.com/c058f544c737782deacefa532d9add4c.png',
                 'date_posted': datetime(2014, 10, 24, 14, 31, 57),
                 'waited': 17.211388888888887,
                 'user': 'olivershaw',
                 'html_url': 'https://github.com/bbc/pcs-cloudtools/pull/2'},
                {'repo': {'owner': 'bbc', 'repo': 'app-config-qa'},
                 'assignee': 'jonauman',
                 'num': '93',
                 'avatar': 'https: //identicons.github.com/05f971b5ec196b8c65b75d2ef8267331.png',
                 'date_posted': datetime(2014, 10, 24, 9, 20, 9),
                 'waited': 22.408055555555556,
                 'user': 'gauravsood',
                 'html_url': 'https://github.com/bbc/pcs-cloudtools/pull/1'}]

    unassigned = [{'repo': {'owner': 'bbc', 'repo': 'app-config-qa'},
                   'num': '106',
                   'avatar': 'https: //identicons.github.com/0777d5c17d4066b82ab86dff8a46af6f.png',
                   'date_posted': datetime(2014, 10, 31, 16, 15, 23),
                   'waited': 15.486944444444445,
                   'user': 'charlottephilippe',
                   'html_url': 'https://github.com/bbc/pcs-cloudtools/pull/3'},
                  {'repo': {'owner': 'bbc', 'repo': 'app-config-qa'},
                   'num': '54',
                   'avatar': 'https: //identicons.github.com/0777d5c17d4066b82ab86dff8a46af6f.png',
                   'date_posted': datetime(2014, 10, 31, 16, 31, 6),
                   'waited': 15.225277777777778,
                   'user': 'charlottephilippe',
                   'html_url': 'https://github.com/bbc/pcs-cloudtools/pull/4'}]

    def setUp(self):
        self.app = pull_requests_web.app.test_client()
        pull_requests.pull_requests_web.pr_data = {'team1': (self.assigned, self.unassigned),
                                                   'team2': (self.assigned, self.unassigned)}

    def healthcheck_test(self):
        test_response = self.app.get('/ping/ping')
        check_content_type(test_response.headers, 'text/html')
        eq_(test_response.status_code, 200)

    def dynamic_endpoint_test(self):
        for group_config in default_repos:
            # Given:
            # mock the get_requests method so we can mock GitHub
            mocked_get_requests_method = MagicMock()
            mocked_get_requests_method.return_value = (self.unassigned, self.assigned)
            pull_requests_web.get_requests = mocked_get_requests_method

            # When
            test_response = self.app.get('/pulls/{group}'.format(group=group_config['group']))

            # Then
            check_content_type(test_response.headers, 'text/html')
            eq_(test_response.status_code, 200)
            mocked_get_requests_method.assert_called_with(group_config['watches'])

            for assigned_request in self.assigned:
                self.assert_h4_containing_text(test_response.data, assigned_request['repo']['repo'] + " #" + assigned_request['num'])
            for unassigned_request in self.unassigned:
                self.assert_h4_containing_text(test_response.data, unassigned_request['repo']['repo'] + " #" + unassigned_request['num'])

    def non_existent_endpoint_test(self):
        test_response = self.app.get('/non-existent')
        eq_(test_response.status_code, 404)
        check_content_type(test_response.headers, 'text/html')
        soup = BeautifulSoup(test_response.data)
        eq_(soup.title.string, 'Not Found - Pull Request Dashboard')
        group_names = [config_item['group'] for config_item in default_repos]
        for group_name in group_names:
            self.assert_link(test_response.data, "/pulls/{group_name}".format(group_name=group_name), group_name)

    def assert_h4_containing_text(self, html, text):
        h4s = BeautifulSoup(html).findAll('h4')
        match_found = False
        for h4 in h4s:
            if h4.text == text:
                match_found = True
                break
        eq_(match_found, True, "h4 with text {} was expected but not found".format(text))

    def assert_link(self, html, href, text):
        links = BeautifulSoup(html).findAll('a')
        match_found = False
        for link in links:
            if link.text == text and link.get('href') == href:
                match_found = True
                break
        eq_(match_found, True, "Link with href {} and text {} was expected but not found".format(href, text))
