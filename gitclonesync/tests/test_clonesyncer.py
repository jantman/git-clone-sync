from gitclonesync.clonesyncer import CloneSyncer, UPSTREAM_NAMES, parse_args, cli_entry
from gitclonesync.githubclone import GitHubKeyError

from contextlib import nested
from mock import patch, call, MagicMock
import pytest
import logging
import sys


class Container:
    pass


@pytest.fixture
def mocklogger():
    ml = MagicMock(name='mocklogger', spec_set=logging.Logger)
    return ml


class TestCloneSyncer:

    def test_init_defaults(self, mocklogger):
        """ test init with defaults """
        mock_ghc = MagicMock(spec_set='gitclonesync.githubclone.GitHubClone')
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer._check_versions', autospec=True),
                patch('gitclonesync.clonesyncer.GitHubClone', autospec=True),
        ) as (mock_getlogger, mock_checkver, mock_ghc_init):
            mock_getlogger.return_value = mocklogger
            mock_ghc_init.return_value = mock_ghc
            cs = CloneSyncer('/foo/bar')
            assert cs.path == '/foo/bar'
            assert cs.dryrun == False
            assert cs.logger == mocklogger
            assert mock_checkver.call_count == 1
            assert mocklogger.call_count == 0
            assert cs.sync_dirty == False
            assert cs.origin_only == False
            assert cs.no_upstream == False
            assert mock_ghc_init.mock_calls == [call()]
            assert mock_ghc.mock_calls == []

    def test_init_gh_no_key(self, mocklogger):
        """ test init with no github creds (GitHubClient raises exception) """
        mock_ghc = MagicMock(spec_set='gitclonesync.githubclone.GitHubClone')
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer._check_versions', autospec=True),
                patch('gitclonesync.clonesyncer.GitHubClone', autospec=True),
        ) as (mock_getlogger, mock_checkver, mock_ghc_init):
            mock_getlogger.return_value = mocklogger
            mock_ghc_init.side_effect = GitHubKeyError
            cs = CloneSyncer('/foo/bar')
            assert cs.path == '/foo/bar'
            assert mock_checkver.call_count == 1
            assert cs.gh is None
            assert mocklogger.error.call_args_list == [
                call("ERROR: Unable to find GitHub API Key, disabling GitHub API integration.")
            ]

    def test_init_dryrun(self, mocklogger):
        """ test init with defaults """
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer._check_versions', autospec=True),
        ) as (mock_getlogger, mock_checkver):
            mock_getlogger.return_value = mocklogger
            cs = CloneSyncer('/foo/bar', dryrun=True)
            assert cs.path == '/foo/bar'
            assert cs.dryrun == True
            assert mocklogger.warning.call_args_list == [
                call("Running in dryrun mode - will not make any changes on disk")
            ]

    def test_init_disable_github(self, mocklogger):
        """ test init with github disabled """
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer._check_versions', autospec=True),
        ) as (mock_getlogger, mock_checkver):
            mock_getlogger.return_value = mocklogger
            cs = CloneSyncer('/foo/bar', disable_github=True)
            assert cs.path == '/foo/bar'
            assert cs.gh is None
            assert mocklogger.warning.call_args_list == [
                call("Disabling all GitHub API integration per disable_github option")
            ]


class TestCloneSyncerCLI:

    @pytest.fixture
    def defaultargs(self):
        a = Container()
        setattr(a, 'directory', '/path/to/cwd')
        setattr(a, 'dry_run', False)
        setattr(a, 'verbose', False)
        setattr(a, 'quiet', False)
        setattr(a, 'sync_dirty', False)
        setattr(a, 'disable_github', False)
        setattr(a, 'origin_only', False)
        setattr(a, 'no_upstream', False)
        return a

    def test_cli_entry_default(self, mocklogger, defaultargs):
        """ test default cli_entry() with no args """
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.parse_args', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_parse_args, mock_cs):
            mock_parse_args.return_value = defaultargs
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mock_parse_args.call_count == 1
            assert mocklogger.called is False
            assert mock_cs.mock_calls == [
                call(path='/path/to/cwd',
                     dryrun=False,
                     sync_dirty=False,
                     disable_github=False,
                     origin_only=False,
                     no_upstream=False),
                call().run(),
            ]

    def test_cli_entry_quiet(self, mocklogger, defaultargs):
        """ test cli_entry() with -q argument """
        defaultargs.quiet = True
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.parse_args', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_parse_args, mock_cs):
            mock_parse_args.return_value = defaultargs
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mock_parse_args.call_count == 1
            assert mocklogger.setLevel.call_args_list == [call(logging.WARNING)]
            assert mock_cs.mock_calls == [
                call(path='/path/to/cwd',
                     dryrun=False,
                     sync_dirty=False,
                     disable_github=False,
                     origin_only=False,
                     no_upstream=False),
                call().run(),
            ]

    def test_cli_entry_all_args(self, mocklogger, defaultargs):
        """ test cli_entry() with all args """
        defaultargs.directory = '/foo/bar'
        defaultargs.dry_run = True
        defaultargs.verbose = True
        defaultargs.sync_dirty = True
        defaultargs.disable_github = True
        defaultargs.origin_only = True
        defaultargs.no_upstream = True
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('gitclonesync.clonesyncer.parse_args', autospec=True),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_parse_args, mock_cs):
            mock_parse_args.return_value = defaultargs
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mock_parse_args.call_count == 1
            assert mocklogger.setLevel.call_args_list == [call(logging.DEBUG)]
            assert mock_cs.mock_calls == [
                call(path='/foo/bar',
                     dryrun=True,
                     sync_dirty=True,
                     disable_github=True,
                     origin_only=True,
                     no_upstream=True),
                call().run(),
            ]

    def test_parse_args_specified_dir(self, defaultargs):
        """ test parse_args() with specified directory and verbose """
        defaultargs.directory = '/foo/bar/baz'
        defaultargs.verbose = True
        argv = ['git_clone_sync', '-v', '/foo/bar/baz']
        with nested(
                patch.object(sys, 'argv', argv),
                patch('gitclonesync.clonesyncer.os.getcwd', autospec=True),
        ) as (patch_argv, mock_getcwd):
            mock_getcwd.return_value = '/path/to/cwd'
            res = parse_args(argv)
            assert mock_getcwd.call_count == 1
            assert vars(res) == vars(defaultargs)

    def test_parse_args_defaults(self, defaultargs, monkeypatch):
        """ test parse_args() with defaults only """
        argv = ['git_clone_sync']
        with nested(
                patch.object(sys, 'argv', argv),
                patch('gitclonesync.clonesyncer.os.getcwd', autospec=True),
        ) as (patch_argv, mock_getcwd):
            mock_getcwd.return_value = '/path/to/cwd'
            res = parse_args(argv)
            assert mock_getcwd.call_count == 1
            assert vars(res) == vars(defaultargs)

    def test_parse_args_all_options(self, defaultargs):
        """ test parse_args() with all options """
        defaultargs.dry_run = True
        defaultargs.quiet = True
        defaultargs.sync_dirty = True
        defaultargs.disable_github = True
        defaultargs.origin_only = True
        defaultargs.no_upstream = True
        argv = ['git_clone_sync',
                '-d',
                '-q',
                '-D',
                '-G',
                '-o',
                '-u']
        with nested(
                patch.object(sys, 'argv', argv),
                patch('gitclonesync.clonesyncer.os.getcwd', autospec=True),
        ) as (patch_argv, mock_getcwd):
            mock_getcwd.return_value = '/path/to/cwd'
            res = parse_args(argv)
            assert mock_getcwd.call_count == 1
            assert vars(res) == vars(defaultargs)
