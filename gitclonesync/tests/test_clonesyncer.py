from gitclonesync.clonesyncer import CloneSyncer, UPSTREAM_NAMES, parse_args, cli_entry

from contextlib import nested
from mock import patch, call, MagicMock
import pytest
import logging


class TestCloneSyncer:

    @pytest.fixture
    def mocklogger(self):
        ml = MagicMock(name='mocklogger', spec_set=logging.Logger)
        return ml

    def test_cli_entry_default(self, mocklogger):
        """ test default cli_entry() with no args """
        argv = ['git_clone_sync']
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('sys.argv', argv),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
                patch('os.getcwd', autospec=True),
        ) as (mock_getlogger, mock_argv, mock_cs, mock_getcwd):
            mock_getcwd.return_value = '/path/to/cwd'
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mock_getcwd.call_count == 1
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

    def test_cli_entry_verbose(self, mocklogger):
        """ test cli_entry() with -v argument """
        argv = ['git_clone_sync', '-v']
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('sys.argv', argv),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_argv, mock_cs):
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mocklogger.setLevel.call_args_list == [call(logging.DEBUG)]

    def test_cli_entry_quiet(self, mocklogger):
        """ test cli_entry() with -q argument """
        argv = ['git_clone_sync', '-q']
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('sys.argv', argv),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_argv, mock_cs):
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
            assert mocklogger.setLevel.call_args_list == [call(logging.WARNING)]

    def test_cli_entry_all_args(self, mocklogger):
        """ test cli_entry() with all args """
        argv = ['git_clone_sync',
                '-d',
                '-v',
                '-D',
                '-G',
                '-o',
                '-u',
                '/foo/bar',
        ]
        with nested(
                patch('logging.getLogger', autospec=True),
                patch('sys.argv', argv),
                patch('gitclonesync.clonesyncer.CloneSyncer', autospec=True),
        ) as (mock_getlogger, mock_argv, mock_cs):
            mock_getlogger.return_value = mocklogger
            cli_entry()
            assert mock_getlogger.mock_calls == [call()]
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
