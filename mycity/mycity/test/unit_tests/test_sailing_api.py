"""Tests the weather API service at Community Boating Inc"""

import unittest
import sys

sys.path.append('../../../')

from mycity.intents.sailing_weather_intent import get_sailing_conditions


YELLOW_CASE = ("The sailing conditions are currently yellow at Community Boating.")
CLOSED_CASE = ("Community Boating is currently closed.")
ERROR_CASE = ("Sailing weather information for Community Boating is currently unavailable. Please try again later.")


class TestSailingIntent(unittest.TestCase):
    """Test valid and error cases of the Sailing Weather Intent"""
    
    def test_valid(self):
        # print(get_sailing_conditions('var FLAG_COLOR = "Y"'))
        self.assertEqual(get_sailing_conditions('var FLAG_COLOR = "Y"'),YELLOW_CASE)

    def test_invalid(self):
        # print(get_sailing_conditions('Blah blah blah, garbage response'))
        self.assertEqual(get_sailing_conditions('Blah blah blah, garbage response'),ERROR_CASE)
        
    def test_no_resp(self):
        # print(get_sailing_conditions(''))
        self.assertEqual(get_sailing_conditions(''),ERROR_CASE)
        
    def test_no_resp(self):
        # print(get_sailing_conditions([]))
        self.assertEqual(get_sailing_conditions([]),ERROR_CASE)
        
    def test_no_resp(self):
        # print(get_sailing_conditions({}))
        self.assertEqual(get_sailing_conditions({}),ERROR_CASE)
        
    def test_no_resp(self):
        # print(get_sailing_conditions(0))
        self.assertEqual(get_sailing_conditions(0),ERROR_CASE)

    def test_closed(self):
        # print(get_sailing_conditions('var FLAG_COLOR = "C"'))
        self.assertEqual(get_sailing_conditions('var FLAG_COLOR = "C"'),CLOSED_CASE)