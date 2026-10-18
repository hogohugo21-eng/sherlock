import csv
from unittest.mock import Mock

import pytest
from openpyxl import load_workbook
from sherlock_project import sherlock
from sherlock_project.result import QueryResult, QueryStatus


@pytest.mark.parametrize('option', ['--csv', '--xlsx'])
def test_export_does_not_create_formulas(tmp_path, monkeypatch, option):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sys.argv', ['sherlock', '=1+1', option, '--local'])
    monkeypatch.setattr(sherlock, 'http_get', Mock(side_effect=RuntimeError('offline')))
    monkeypatch.setattr(sherlock, 'SitesInformation', Mock(return_value=Mock(__iter__=lambda self: iter([]))))
    result = QueryResult('=1+1', '=2+2', '=3+3', QueryStatus.CLAIMED, query_time=0.1)
    monkeypatch.setattr(sherlock, 'sherlock', Mock(return_value={
        '=2+2': {'status': result, 'url_main': '=3+3', 'url_user': '=4+4', 'http_status': 200}
    }))
    sherlock.main()
    if option == '--csv':
        with next(tmp_path.glob('*.csv')).open(newline='', encoding='utf-8') as f:
            row = list(csv.reader(f))[1]
        assert row[:4] == ["'=1+1", "'=2+2", "'=3+3", "'=4+4"]
    else:
        book = load_workbook(next(tmp_path.glob('*.xlsx')))
        try:
            assert all(cell.data_type != 'f' for row in book.active for cell in row)
        finally:
            book.close()
