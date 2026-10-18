from unittest.mock import Mock
from werkzeug.wrappers import Response

from sherlock_project.sherlock import sherlock


def test_search_does_not_send_local_netrc(tmp_path, monkeypatch, httpserver):
    netrc = tmp_path / 'netrc'
    netrc.write_text('machine localhost login PRIVATE_USER password PRIVATE_PASSWORD\n')
    monkeypatch.setenv('NETRC', str(netrc))
    monkeypatch.setenv('NO_PROXY', '*')
    seen = []

    def handler(request):
        seen.append(request.headers.get('Authorization'))
        return Response('profile')

    httpserver.expect_request('/test').respond_with_handler(handler)
    url = httpserver.url_for('/').replace('127.0.0.1', 'localhost')
    results = sherlock('test', {'Local': {'urlMain': url, 'url': url + '{}', 'errorType': 'status_code'}}, Mock(), timeout=5)
    assert results['Local']['http_status'] == 200
    assert seen == [None]
