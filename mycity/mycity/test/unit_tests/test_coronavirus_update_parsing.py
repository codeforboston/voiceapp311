"""
Test parsing utilities of the CoronavirusUpdateIntent. 

These tests rely on sample data in this repository. If the real
website changes format, it should be caught by integration
tests and the sample will need to be updated.
"""

import mycity.intents.coronavirus_update_intent as coronavirus_update_intent
import mycity.test.unit_tests.base as base

from bs4 import BeautifulSoup
import os
import unittest.mock as mock


def _get_test_data_parser(file_name):
    test_file_path = os.path.join(os.getcwd(),
                                  "mycity/test/test_data", file_name)
    with open(test_file_path) as f:
        parser = BeautifulSoup(f.read(), 'html.parser')
        return parser


class CoronavirusUpdateParserTest(base.BaseTestCase):

    @mock.patch('mycity.intents.coronavirus_update_intent._get_html_parser')
    def test_boston_homepage_parse(self, mock_get_html_parser):
        print(os.getcwd())
        parser = _get_test_data_parser('Boston.gov.html')
        mock_get_html_parser.return_value = parser
        output_speech = coronavirus_update_intent._get_homepage_text()
        self.assertTrue(output_speech)

    @mock.patch('mycity.intents.coronavirus_update_intent._get_html_parser')
    def test_boston_coronavirus_detail_parse(self, mock_get_html_parser):
        parser = _get_test_data_parser('CoronavirusDiseaseinBoston.gov.html')
        mock_get_html_parser.return_value = parser
        output_speech = coronavirus_update_intent._get_coronavirus_detail_text()
        self.assertTrue(output_speech)
