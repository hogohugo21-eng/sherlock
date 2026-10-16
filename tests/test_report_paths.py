"""Usernames are data, never output paths."""
from unittest.mock import Mock

import pytest
from sherlock_project import sherlock


@pytest.mark.parametrize('option,extension', [('--txt', 'txt'), ('--csv', 'csv'), ('--xlsx', 'xlsx')])
def test_username_cannot_escape_output_directory(tmp_path, monkeypatch, option, extension):
    output = tmp_path / 'reports'
    output.mkdir()
    monkeypatch.chdir(output)
    monkeypatch.setattr('sys.argv', ['sherlock', '../outside', option, '--local'])
    monkeypatch.setattr(sherlock.requests, 'get', Mock(side_effect=RuntimeError('offline')))
    monkeypatch.setattr(sherlock, 'SitesInformation', Mock(return_value=Mock(__iter__=lambda self: iter([]))))
    monkeypatch.setattr(sherlock, 'sherlock', Mock(return_value={}))
    sherlock.main()
    assert not (tmp_path / f'outside.{extension}').exists()
    assert len(list(output.glob(f'*.{extension}'))) == 1
