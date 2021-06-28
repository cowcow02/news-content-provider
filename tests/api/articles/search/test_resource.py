from http import HTTPStatus
from unittest.mock import patch, Mock

import mongo


def patch_mongo(*args, **kwargs):
    return patch.object(mongo, *args, *kwargs)


class TestGet:
    def test_that_it_returns_ok_status_code(self, client):
        mocked_mongo = Mock(return_value=([]))
        with patch_mongo('search_articles_by_keyword', mocked_mongo):
            response = client.get('/articles/search', query_string={'q': 'hello'})
        assert response.status_code == HTTPStatus.OK

    def test_that_it_returns_correct_data(self, client):
        mocked_mongo = Mock(return_value=([]))
        with patch_mongo('search_articles_by_keyword', mocked_mongo):
            response = client.get('/articles/search', query_string={'q': 'hello'})

        assert response.json == {
            'metadata': {
                'q': 'hello',
            },
            'pagination': {
                'limit': 20,
                'offset': 0,
            },
            'results': [],
        }
