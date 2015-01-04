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


UPSTREAM_NAMES = ['upstream']


class CloneSyncer:
    """
    Main class for syncing git clones
    """

    def __init__(self, path, sync_dirty=False, disable_github=False, origin_only=False, no_upstream=False, dryrun=False):
        """
        init

        :param path: the directory to sync - either the path to a git clone, or a directory containing git clones (non-recursive)
        :type path: string
        :param sync_dirty: if True, also sync dirty clones. Default is False, do not touch dirty clones
        :type sync_dirty: boolean
        :param disable_github: if True, disable all GitHub API integration
        :type disable_github: boolean
        :param origin_only: if True, do not fetch any remotes other than origin
        :type origin_only: boolean
        :param no_upstream: if True, do not push upstream/master to origin/master
        :type no_upstream: boolean
        :param dryrun: if True, don't change anything on disk, just log (at info level) what would be done
        :type dryrun: boolean
        """
        self.dryrun = dryrun
        self.logger = logging.getLogger(self.__class__.__name__)
        self._check_versions()
        if dryrun:
            self.logger.warning("Running in dryrun mode - will not make any changes on disk")
        self.sync_dirty = sync_dirty
        self.path = path
        self.origin_only = origin_only
        self.no_upstream = no_upstream
        if disable_github:
            self.gh = None
        else:
            raise NotImplementedError("try to init github client here")

    def run(self):
        """
        do the actual clone update
        """
        if os.path.isdir(os.path.join(self.path, '.git')):
            logger.info("Syncing {p}".format(p=self.path))
            self._do_git_dir(self.path)
            return
        # else this isn't a git dir itself
        git_dirs = self._get_git_dirs(self.path)
        logger.info("Syncing {n} git directories under {p}".format(n=len(git_dirs), p=self.path))
        for d in git_dirs:
            self._do_git_dir(d)

    def _get_git_dirs(self, path):
        """
        get a list of all git directories under a given path

        :param path: path to check for git directories
        :type path: string
        """
        self.logger.debug("finding git directories under {p}".format(p=path))
        gitdirs = []
        for name in os.listdir(path):
            dirpath = os.path.join(d, name)
            if os.path.isdir(dirpath) and os.path.isdir(os.path.join(dirpath, '.git')):
                if dirpath not in gitdirs:
                    gitdirs.append(dirpath)
        return gitdirs

    def _do_git_dir(self, path):
        """
        sync a single git directory/clone

        :param path: path to the clone
        :type path: string
        """
        self.logger.info("Syncing {p}".format(p=path))
        repo = git.Repo(path)
        if repo.bare:
            logger.warining("Skipping bare repo at %s" % path)
            return False
        if repo.is_dirty():
            if self.sync_dirty:
                raise NotImplementedError("TODO: implement what to do with dirty repos")
            else:
                self.logger.warning("Skipping dirty repo: %s" % path)
                return False
        # ok, repo isn't bare or dirty
        current_branch = repo.active_branch
        self.logger.debug("current branch is %s" % current_branch)

        if self.gh is not None:
            on_github = False
            for rmt in repo.remotes:
                if 'github.com' in rmt.url:
                    on_github = True
                    break
            if on_github:
                raise NotImplementedError('TODO - guard this with a config setting?')
                # do_github_repo(repo, config, gh_client, dryrun=False)

        upstream = None
        for rmt in repo.remotes:
            if rmt.name != 'origin' and self.origin_only:
                logger.debug("skipping non-origin remote '{r}'".format(r=rmt.name))
                continue
            self._fetch_remote(rmt)
            if rmt.name in UPSTREAM_NAMES and not self.no_upstream:
                upstream = rmt

        # guard with config setting TODO
        if repo.is_dirty(untracked_files=True):
            self.logger.warning("Repo has untracked files, not switching branches.")
            return False
        if 'master' not in repo.branches:
            self.logger.warning("Repo has no 'master' branch; skipping further work")
            return False
        raise NotImplementedError("wrap the upstream-to-origin branch sync logic in a func, so we can do for *all* branches in both remotes")
        # checkout master, pull
        if current_branch != 'master':
            self._checkout_branch(repo, 'master')
        self._pull_remote(repo, 'origin')
        # if we have an upstream to pull from, do that, then push to origin
        if upstream is not None:
            self._pull_remote(repo, upstream.name)
            self._push_remotr(repo, 'origin')
        # switch back to original branch
        self._checkout_branch(repo, current_branch)
        return True

    def _pull_remote(self, repo, rmtname):
        """ pull from a remote """
        if self.dryrun:
            self.logger.info("DRYRUN - would pull remote '{r}'".format(r=rmtname))
            return
        self.logger.debug("pulling remote '{r}'".format(r=rmtname))
        repo.remote(name=rmtname).pull()

    def _push_remote(self, repo, rmtname):
        """ push from a remote """
        if self.dryrun:
            self.logger.info("DRYRUN - would push to remote '{r}'".format(r=rmtname))
            return
        self.logger.debug("pushing to remote '{r}'".format(r=rmtname))
        repo.remote(name=rmtname).push()

    def _checkout_branch(self, repo, branchname):
        """ check out a branch """
        if self.dryrun:
            self.logger.info("DRYRUN - would check out branch '{b}'".format(b=branchname))
            return
        self.logger.debug("checking out branch '{b}'".format(b=branchname))
        b = getattr(repo.heads, branchname)
        b.checkout()

    def _fetch_remote(self, rmt):
        """ fetch a remote """
        if self.dryrun:
            self.logger.info("DRYRUN - would fetch rmt '%s'" % rmt.name)
            return
        self.logger.debug("fetching remote '%s'" % rmt.name)
        rmt.fetch()

    def _check_versions(self):
        """
        checks that requirements have supported versions

        this is mainly needed for GitPython, where we rely on features
        in the 0.3.2.1 version

        thanks to @qwcode for this simple logic
        """
        gp_req_str = 'GitPython>=0.3.2.1'
        gp_req = pkg_resources.Requirement.parse(gp_req_str)
        gp_dist = pkg_resources.get_distribution('GitPython')
        self.logger.debug("Checking GitPython requirement")
        if gp_dist not in gp_req:
            raise SystemExit("ERROR: gitclonesync requires %s" % gp_req_str)
        self.logger.debug("All requirements satisfied")
        return True


def parse_args(argv):
    """ parse arguments with OptionParser """
    parser = argparse.ArgumentParser(description='Sync local git clones')
    parser.add_argument('directory', metavar='PATH', type=str, default=os.getcwd(),
                        help='path to git clone or directory of clones (default ./)')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', default=False,
                        help='do not make any changes on disk, just log what would be done')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='debug-level output on what actions are being taken')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False,
                        help='suppress all logging below WARNING level')
    parser.add_argument('-D', '--sync-dirty', dest='sync_dirty', action='store_true', default=False,
                        help='sync dirty clones; default is to not touch dirty clones')
    parser.add_argument('-G', '--no-github', dest='disable_github', action='store_true', default=False,
                        help='disable GitHub API integration')
    parser.add_argument('-o', '--only-origin', dest='origin_only', action='store_true', default=False,
                        help='only fetch origin, not any other remotes')
    parser.add_argument('-u', '--no-upstream', dest='no_upstream', action='store_true', default=False,
                        help='do not push upstream/master to origin/master')
    args = parser.parse_args(argv)
    return args


def cli_entry():
    """
    CLI script entry point
    """
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s")
    logger = logging.getLogger()
    args = parse_args(sys.argv)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.WARNING)

    cs = CloneSyncer(path=args.directory, dryrun=args.dry_run, sync_dirty=args.sync_dirty, disable_github=args.disable_github, origin_only=args.origin_only, no_upstream=args.no_upstream)
    cs.run()
