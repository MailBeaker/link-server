import unittest

from mock import patch

from main import app
from views import MB_HOMEPAGE
from sdk import constants

API_VERSION = 'v1'
VALID_JWT = 'eyJpIjoiOGZmMTlhYWNhZjE3NWRkNTExM2VkOGZiIiwidSI6Imh0dHA6Ly9nb29nbGUuY29tIn0.MEUCIH1v4xx82oCnyKZ8zd21mcs3V7aTHFbiGY0-Kr0JAV8YAiEA9CPboQEX7t-TzrCq8t1GPrMfK9wYqFH2At2z5eYXIcA'
INVALID_JWT = 'byJpIjoiOGZmMTlhYWNhZjE3NWRkNTExM2VkOGZiIiwidSI6Imh0dHA6Ly9nb29nbGUuY2'
LINK = 'http://google.com'

class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        assert 302 == rv.status_code
        assert MB_HOMEPAGE == rv.headers['Location']

    def test_missing_jwt(self):
        rv = self.app.get('/' + API_VERSION)
        assert 404 == rv.status_code

    @patch('utils.get_link_info')
    def test_valid_jwt(self, get_link_info):
        get_link_info.return_value = constants.ACTION_PASS, LINK

        rv = self.app.get('/' + API_VERSION + '/' + VALID_JWT + '/')

        get_link_info.assert_called_once_with(VALID_JWT)
        assert 302 == rv.status_code
        assert LINK == rv.headers['Location']

    @patch('utils.get_link_info')
    def test_warned_link(self, get_link_info):
        get_link_info.return_value = constants.ACTION_WARN, LINK

        rv = self.app.get('/' + API_VERSION + '/' + VALID_JWT + '/')

        get_link_info.assert_called_once_with(VALID_JWT)
        assert 200 == rv.status_code
        assert b'We&#39;ve got a bad feeling about this.' in rv.data

    @patch('utils.get_link_info')
    def test_blocked_link(self, get_link_info):
        get_link_info.return_value = constants.ACTION_BLOCK, LINK

        rv = self.app.get('/' + API_VERSION + '/' + VALID_JWT + '/')

        get_link_info.assert_called_once_with(VALID_JWT)
        assert 200 == rv.status_code
        assert b'We&#39;re stepping in to protect you.' in rv.data

    @patch('utils.get_link_info')
    def test_invalid_jwt(self, get_link_info):
        get_link_info.return_value = constants.ACTION_INVALID, None

        rv = self.app.get('/' + API_VERSION + '/' + INVALID_JWT + '/')

        get_link_info.assert_called_once_with(INVALID_JWT)
        assert 400 == rv.status_code

