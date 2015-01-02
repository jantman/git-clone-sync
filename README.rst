git-clone-sync
==============

.. image:: https://pypip.in/v/gitclonesync/badge.png
   :target: https://crate.io/packages/gitclonesync

.. image:: https://pypip.in/d/gitclonesync/badge.png
   :target: https://crate.io/packages/gitclonesync


.. image:: https://secure.travis-ci.org/jantman/gitclonesync.png?branch=master
   :target: http://travis-ci.org/jantman/gitclonesync
   :alt: travis-ci for master branch

.. image:: https://codecov.io/github/jantman/gitclonesync/coverage.svg?branch=master
   :target: https://codecov.io/github/jantman/gitclonesync?branch=master
   :alt: coverage report for master branch

.. image:: http://www.repostatus.org/badges/0.1.0/wip.svg
   :alt: Project Status: Wip - Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
   :target: http://www.repostatus.org/#wip

Script to keep git clones in sync with origin and upstream, and optinally keep origin master in sync with upstream.

Licensed under the GNU General Public License version 3 or later.

Features
---------

* Optionally fail/exit if one of a list of shell commands fail (use to ensure that ssh-agent
  must be running, VPN connection must be up, etc.).
* Operate on all git repos in specified directories non-recursively.
* Fetch origin for each git repo found.
* Optionally switch to master branch and pull (controlled globally via ENABLE_PULL
  and per-repo via REPO_OPTIONS)
* If using github API (see below):
  * Add fetch refs to fetch PRs as branches.
  * If the repo is a fork, add a remote for the upstream (parent). Optionally, pull
    master on the upstream and push back to origin (keep origin master in sync with
    upstream).

Requirements
------------

* Unfortunately, Python 2.x only (2.6+) as those are the versions supported by `GitPython <https://pypi.python.org/pypi/GitPython>`_
* `GitPython <https://pypi.python.org/pypi/GitPython>`_ 0.3.2.1 or later
* `github3.py <https://pypi.python.org/pypi/github3.py>`_ 0.8.2 or later

_Note:_ Versions of GitPython prior to 0.3.2.1 had a `bug <https://github.com/gitpython-developers/GitPython/issues/28>`_
in the parsing of FETCH_INFO which caused it to raise an exception when fetching from
any repository that has a remote configured with a non-branch, non-tag refspec,
such as the ones used by GitHub (``refs/pull/*/head``) to check out pull requests.

Installation
------------

It's recommended that you install into a virtual environment (virtualenv /
venv). See the `virtualenv usage documentation <http://www.virtualenv.org/en/latest/>`_
for information on how to create a venv. If you really want to install
system-wide, you can (using sudo).

.. code-block:: bash

    pip install gitclonesync

Configuration
--------------

Configuration is stored as JSON, in a text configuration file at
``~/.sync_git_clones.conf.py`` by default. Running this script without an existing
configuration file and with the ``-g`` option will cause it to write a sample config
file to disk, for you to edit.

The configuration file supports the following keys:
* __gitdirs__ - (list of strings) a list of directories to search _non_-recursively for
  git directories/clones. These will be passed through os.path.expanduser and
  os.pathabspath before being used.
* __skipdirty__ - (boolean) If true, skip past dirty repos and log an error.
* __only_fetch_origin__ - (boolean) If true, only fetch a remote called "origin".
  Otherwise, fetch all remotes.
* __github__ - (boolean) whether to enable GitHub API integration.

If you want to use the GitHub API integration, you should have an API key/token available.
This script will parse ~/.gitconfig using the ConfigParser module, looking for github.token
as explained in the [Local GitHub Config blog post](https://github.com/blog/180-local-github-config).

Usage
-----


Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/gitclonesync/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on as my time and priority allows.

License
-------

gitclonesync is licensed under the `GNU General Public
License <http://www.gnu.org/licenses/gpl-3.0.html>`_ version 3, with the
additional term that the Copyright and Authors attributions may not be removed
or otherwise altered, except to add the Author attribution of a contributor to
the work. (Additional Terms pursuant to Section 7b of the GPL v3).

Development
===========

To install for development:

1. Fork the `gitclonesync <https://github.com/jantman/gitclonesync>`_ repository on GitHub
2. Create a new branch off of master in your fork.

.. code-block:: bash

    $ virtualenv gitclonesync
    $ cd gitclonesync && source bin/activate
    $ pip install -e git+git@github.com:YOURNAME/gitclonesync.git@BRANCHNAME#egg=gitclonesync
    $ cd src/gitclonesync

The git clone you're now in will probably be checked out to a specific commit,
so you may want to ``git checkout BRANCHNAME``.

Guidelines
----------

* pep8 compliant with some exceptions (see pytest.ini)

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`_, driven by `tox <http://tox.testrun.org/>`_.

* testing is as simple as:

  * ``pip install tox``
  * ``tox``

* If you want to see code coverage: ``tox -e cov``

  * this produces two coverage reports - a summary on STDOUT and a full report in the ``htmlcov/`` directory

* If you want to pass additional arguments to pytest, add them to the tox command line after "--". i.e., for verbose pytext output on py27 tests: ``tox -e py27 -- -v``

Release Checklist
-----------------

1. Open an issue for the release; cut a branch off master for that issue.
2. Confirm that there are CHANGES.rst entries for all major changes.
3. Ensure that Travis tests passing in all environments.
4. Ensure that test coverage is no less than the last release (ideally, 100%).
5. Increment the version number in gitclonesync/__init__.py and add version and release date to CHANGES.rst, then push to GitHub.
6. Confirm that README.rst renders correctly on GitHub.
7. Upload package to testpypi, confirm that README.rst renders correctly.

   * Make sure your ~/.pypirc file is correct
   * ``python setup.py register -r https://testpypi.python.org/pypi``
   * ``python setup.py sdist upload -r https://testpypi.python.org/pypi``
   * Check that the README renders at https://testpypi.python.org/pypi/gitclonesync

8. Create a pull request for the release to be merge into master. Upon successful Travis build, merge it.
9. Tag the release in Git, push tag to GitHub:

   * tag the release. for now the message is quite simple: ``git tag -a vX.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * push the tag to GitHub: ``git push origin vX.Y.Z``

11. Upload package to live pypi:

    * ``python setup.py sdist upload``

10. make sure any GH issues fixed in the release were closed.
