"""
Class for dealing with GitHub API,
w/r/t clones
"""


class GitHubKeyError(Exception):
    """
    Exception for missing GitHub API Key
    """
    pass


class GitHubClone:
    """
    Class for dealing with GitHub clones
    """

    def __init__(self):
        # try to get credentials, raise exception with helpful message if we can't
        pass

    def do_github_repo(self, repo, config, gh_client, dryrun=False):
        """
        operate on a single git directory/clone of a GitHub repo
        :param repo: a GitPython Repository object, passed in from do_git_dir
        :type path: Repository
        :param config: config dict
        :type config: dict
        :param gh_client: TODO
        :param dryrun: if true, do not change anything; log actions that would be taken
        :type dryrun: boolean
        """
        raise SystemExit("Do GitHub stuff here")

    def get_github_client(self, config, dryrun=False):
        """ read API key from git config and return a <TODO> github client instance """
        # `git config --global github.token` and trim that, make sure it's 40 characters
        # try to instantiate API client, and connect
        # return client object
        return None
