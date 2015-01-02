"""
gitclonesync syncer class
"""

import argparse
import sys
import logging
import os.path
import json
import git

# prefer the pip vendored pkg_resources
try:
    from pip._vendor import pkg_resources
except ImportError:
    import pkg_resources


class CloneSyncer:
    """
    Main class for syncing git clones
    """

    def fetch_remote(self, rmt, dryrun=False):
        """ fetch a remote """
        if dryrun:
            logger.info("DRYRUN - would fetch rmt %s" % rmt.name)
        else:
            print("fetching remote %s" % rmt.name)
            rmt.fetch()
        return True

    def do_git_dir(self, path, config, gh_client=None, dryrun=False):
        """
        operate on a single git directory/clone
        :param path: path to the clone
        :type path: string
        :param config: config dict
        :type config: dict
        :param gh_client: a GitHub API client object (TODO)
        :type gh_client: TODO
        :param dryrun: if true, do not change anything; log actions that would be taken
        :type dryrun: boolean
        """
        logger.info("doing gitdir %s" % path)
        repo = git.Repo(path)
        if repo.bare:
            logger.warining("Skipping bare repo: %s" % path)
            return False
        if repo.is_dirty():
            if config['skipdirty']:
                logger.error("Skipping dirty repo: %s" % path)
                return False
            else:
                raise SystemExit("TODO: implement what to do with dirty repos")
        # ok, repo isn't bare or dirty
        current_branch = repo.active_branch
        logger.debug("current branch is %s" % current_branch)

        on_github = False
        for rmt in repo.remotes:
            if 'github.com' in rmt.url:
                on_github = True

        if on_github:
            # TODO - guard this with a config setting?
            do_github_repo(repo, config, gh_client, dryrun=False)

        for rmt in repo.remotes:
            if rmt.name != 'origin' and config['only_fetch_origin']:
                logger.debug("skipping remote %s - only_fetch_origin" % rmt.name)
                continue
            fetch_remote(rmt, dryrun=dryrun)
            if 'github.com' in rmt.url:
                on_github = True

        # guard with config setting TODO
        # if branch is not master, switch to master; pull; switch back to original branch

        return True

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

    def main(configpath='~/.sync_git_clines.conf.py', dryrun=False, genconfig=False):
        """
        main entry point

        :param config: path to configuration file
        :type config: string
        :param dryrun: if true, do not change anything; log actions that would be taken
        :type dryrun: boolean
        :param genconfig: if config file does not exist, write a sample one and exit
        :type genconfig: boolean
        """
        logger.debug("main called with config=%s" % configpath)
        if dryrun:
            logger.warning("dryrun=True - no changes will actually be made")
        configpath = os.path.abspath(os.path.expanduser(configpath))
        logger.debug("config expanded to '%s'" % configpath)

        if not os.path.exists(configpath):
            logger.debug("config file does not exist")
            if genconfig:
                logger.debug("generating sample config file")
                generate_config(configpath, dryrun=dryrun)
                raise SystemExit("Sample configuration file written to: %s" % configpath)
            else:
                raise SystemExit("ERROR: configuration file does not exist. Run with -g|--genconfig to write a sample config at %s" % configpath)

        # attempt to read JSON config
        config = load_config(configpath)
        logger.debug("config loaded")

        if config['github']:
            gh_client = get_github_client(config, dryrun=dryrun)
        else:
            gh_client = None
            logger.info("github integration disabled by config")

        git_dirs = get_git_dirs(config)
        logger.info("found %d git directories" % len(git_dirs))
        for d in git_dirs:
            do_git_dir(d, config, gh_client=gh_client, dryrun=dryrun)

    def get_git_dirs(self, config):
        """ get a list of all git directories to examine """
        logger.debug("finding git directories")
        gitdirs = []
        for d in config['gitdirs']:
            d = os.path.abspath(os.path.expanduser(d))
            logger.debug("checking %s" % d)
            for name in os.listdir(d):
                path = os.path.join(d, name)
                if os.path.isdir(path) and os.path.isdir(os.path.join(path, '.git')):
                    if path in gitdirs:
                        logger.debug("found git dir but already in list: %s" % path)
                    else:
                        logger.debug("found git dir: %s" % path)
                        gitdirs.append(path)
        return gitdirs

    def check_versions():
        """
        checks that requirements have supported versions

        this is mainly needed for GitPython, where we rely on features
        in the heavily-rewritten 0.3.2RC1 version, which is marked as
        beta / RC. ``pip install GitPython`` currently yields 0.1.7, which
        is utterly useless.

        thanks to @qwcode for this simple logic
        """
        gp_req_str = 'GitPython>=0.3.2.1'
        gp_req = pkg_resources.Requirement.parse(gp_req_str)
        gp_dist = pkg_resources.get_distribution('GitPython')
        logger.debug("Checking GitPython requirement")
        if gp_dist not in gp_req:
            raise SystemExit("ERROR: sync_git_clones.py requires %s" % gp_req_str)
        logger.debug("All requirements satisfied")
        return True

    def load_config(self, configpath):
        """ load the configuration file at configpath """
        logger.debug("loading config from %s" % configpath)
        with open(configpath, 'r') as fh:
            configstr = fh.read()
        config = json.loads(configstr)

        # apply defaults
        defaults = {'skipdirty': True, 'only_fetch_origin': False}
        for k in defaults:
            if k not in config:
                logger.debug("applying default config value for %s" % (k))
                config[k] = defaults[k]
        return config

    def generate_config(self, configpath, dryrun=False):
        """ Write out a sample config file. """
        config = {'gitdirs': ['~/GIT', '/path/to/dir'],
                  'skipdirty': True,
                  'github': True,
        }
        logger.debug("serializing sample config")
        configstr = json.dumps(config, sort_keys=True, indent=4, separators=(',', ': '))
        logger.debug("writing serialized sample config to %s" % configpath)
        if dryrun:
            logger.info("DRYRUN: would have written to %s: \n%s" % (path, configstr))
        else:
            with open(configpath, 'w') as fh:
                fh.write(configstr)
            logger.debug("sample config written")
        return True

def parse_args(argv):
    """ parse arguments with OptionParser """
    parser = optparse.OptionParser()

    parser.add_option('-c', '--config', dest='config', action='store', type='string',
                      default='~/.sync_git_clones.conf.py',
                      help='JSON config file location (default: ~/.sync_git_clones.conf.py)')

    parser.add_option('-t', '--test', dest='test', action='store_true', default=False,
                      help='test / dry-run - do not take any action, print what would be done')

    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help='verbose output on what actions are being taken. Specify twice for debug-level output.')

    parser.add_option('-g', '--gen-config', dest='genconfig', action='store_true', default=False,
                      help='if config file does not exist, generate a sample one and exit')

    options, args = parser.parse_args(argv)
    return options

def cli_entry():
    """
    CLI script entry point
    """
    opts = parse_args(sys.argv)
    if opts.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif opts.verbose == 1:
        logger.setLevel(logging.INFO)
    check_versions()
    main(configpath=opts.config, dryrun=opts.test, genconfig=opts.genconfig)
