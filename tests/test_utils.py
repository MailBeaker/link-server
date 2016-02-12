from mock import patch
from mock import Mock

import json
import unittest

from main import app
from utils import get_link_info


#
# class TestUtils(unittest.TestCase):
#
#     @patch('sdk.cloudant.Client.get')
#     @patch('sdk.cloudant.Client.post')
#     def test_get_link_with_warning(self, cloudant_post, cloudant_get):
#
#         cloudant_get.return_value = {
#             'doc_type':             'Link',
#             'orgdomain_id':         'c5e5869ef346610954997afb226b5a60',
#             'url':                  'http://www.google.com',
#             '_rev':                 '1-6a0de2e528726876ed717d6a94b5e8de',
#             'matching_rule_ids':    ['7bb18ed9f3881f636118fba6cfb14359'],
#             '_id':                  '7b4a9082ad274ab5e54ec21ba00abe72',
#             'message_id':           '3e4843f594563d92d15cb7b7b16a87f0'
#         }
#
#         cloudant_post.return_value = {
#             'rows': [
#                 {
#                     'value': {
#                         'rev': '2-bbb527738f09c7aa5c457817e8ef1659'
#                     },
#                     'id': '7bb18ed9f3881f636118fba6cfb14359',
#                     'key': '7bb18ed9f3881f636118fba6cfb14359',
#                     'doc': {
#                         'doc_type': 'OrgDomainRule',
#                         'receiver_mod': 0,
#                         'subject_value': '',
#                         'sender_value': '',
#                         'sender_mod': 0,
#                         '_rev': '2-bbb527738f09c7aa5c457817e8ef1659',
#                         'null': 'bc30bd03c46fa23b21a00ae4232ec9f5',
#                         'description_value': 'Google Warn',
#                         'domain_name': 'mattslifebytes.com',
#                         'organization_id': 'bc30bd03c46fa23b21a00ae4232ec690',
#                         'body_value': '',
#                         'receiver_value': '',
#                         'body_mod': 0,
#                         'action': 1,
#                         'alert_admins': False,
#                         'url_value': 'google.com',
#                         'url_mod': 3,
#                         '_id': '7bb18ed9f3881f636118fba6cfb14359',
#                         'org_domain_id': 'bc30bd03c46fa23b21a00ae4232ec519',
#                         'subject_mod': 0
#                     }
#                 }
#             ],
#             'total_rows': 98626,
#             'offset': 0
#         }
#
#         link_info = utils.check_link('7b4a9082ad274ab5e54ec21ba00abe72')
#
#         expected_info = {
#             'url': 'http://www.google.com',
#             'action': 1
#         }
#
#         self.assertEquals(link_info, expected_info)
#
#         cloudant_get.assert_called_once_with('7b4a9082ad274ab5e54ec21ba00abe72')
#
#         post_data = {
#             'keys': ['7bb18ed9f3881f636118fba6cfb14359'],
#         }
#         cloudant_post.assert_called_once_with(post_data, '_all_docs?include_docs=true')
#
#     @patch('sdk.cloudant.Client.get')
#     @patch('sdk.cloudant.Client.post')
#     def test_no_matching_rules(self, cloudant_post, cloudant_get):
#
#         cloudant_get.return_value = {
#             'doc_type':             'Link',
#             'orgdomain_id':         'c5e5869ef346610954997afb226b5a60',
#             'url':                  'http://www.google.com',
#             '_rev':                 '1-6a0de2e528726876ed717d6a94b5e8de',
#             'matching_rule_ids':    [],
#             '_id':                  '7b4a9082ad274ab5e54ec21ba00abe72',
#             'message_id':           '3e4843f594563d92d15cb7b7b16a87f0'
#         }
#
#         cloudant_post.return_value = {}
#
#         utils.check_link('7b4a9082ad274ab5e54ec21ba00abe72')
#
#         self.assertFalse(cloudant_post.called)
#
#     @patch('sdk.cloudant.Client.get')
#     @patch('sdk.cloudant.Client.post')
#     def test_no_response_no_encoded_url(self, cloudant_post, cloudant_get):
#
#         cloudant_get.return_value = None
#         cloudant_post.return_value = None
#
#         link_info = utils.check_link('7b4a9082ad274ab5e54ec21ba00abe72')
#         self.assertIsNone(link_info)
#         self.assertFalse(cloudant_post.called)
#
#     @patch('sdk.cloudant.Client.decode_url')
#     @patch('sdk.cloudant.Client.get')
#     @patch('sdk.cloudant.Client.post')
#     def test_encoded_url(self, cloudant_post, cloudant_get, cloudant_decode):
#
#         DECODED_URL = 'http://www.google.com'
#
#         cloudant_get.return_value = None
#         cloudant_post.return_value = None
#         cloudant_decode.return_value = DECODED_URL
#
#         link_info = utils.check_link(
#             '7b4a9082ad274ab5e54ec21ba00abe72',
#             encoded_url='0zXR31jG4oU8GSJQMIjxUaNcBvbzh'
#         )
#
#         self.assertEquals(link_info['url'], DECODED_URL)
#         self.assertFalse(cloudant_post.called)
