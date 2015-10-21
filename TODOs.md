# TODOs

* Rebase all HMRC commits
* Add a license: http://choosealicense.com/
* Make the /pulls URL configurable (with a sensible default)
* Catch 'Bad Credentials' error and display a useful page.
* Run under HTTPS
** https://docs.python.org/2/library/ssl.html#ssl.create_default_context
** http://flask.pocoo.org/snippets/111/
* X.509 auth
* Make it possible to specify a 'team' or 'organisation' as a group and therefore to list all that team or orgs PRs on that group page.
* Introduce a pluggable persistence layer which allows us to store the PR data service it from there.
* Configure JSON logging as per standard WebOps conventions.
* Move app startup and config reading to their own method and blow up with a useful error if we can't configure the app sufficiently that it will run.
* Tidy up app config loading method (remove unused stuff)
* If only one group is specified then redirect the index page to that group?
