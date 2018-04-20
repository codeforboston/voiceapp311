import os
import sys

# TODO: running test_suite will only work when executed from this dir
# Configure test dir/suite so tests can be run from deploy_tools
sys.path.insert(0, os.getcwd() + '/../') # this seems kludgy. sure there's a better way
                                 # to do this
sys.path.insert(0, os.getcwd() + '/../intents')

import ast
from intents import intent_constants
from intents import location_utils
from mycity_data_model import MyCityDataModel
import unittest


PARKING_LOTS_TEST_DATA = os.getcwd() + "/test_data/parking_lots"
PARKING_LOTS_ADDR_INDEX = 7

############################################################
# functions for pulling saved test data from "/test_data"  #
############################################################


def get_test_data(comment_tag, filename):
    """
    Reads test data from file that separates datum with newlines

    :param comment_tag: character indicating this value is 
     a comment

    : return ret: a list with all test data 
    """
    ret = []
    with open(PARKING_LOTS_TEST_DATA, "r") as f:
        line =  f.readline()
        while line:
            if line[0] == comment_tag:
                pass
            else: 
                ret.append(ast.literal_eval(line.rstrip()))
            line = f.readline()
    return ret

    


#####################################################
# TestCase class for "../intents/location_utils.py" #
#####################################################



class LocationUtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.mcd = MyCityDataModel()

    def change_address(self, new_address):
        self.mcd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            new_address

    def compare_built_address(self, expected_result):
        origin_addr = location_utils.build_origin_address(self.mcd)
        self.assertEqual(origin_addr, expected_result)
 
    def tearDown(self):
        self.mcd = None

    def test_build_origin_address_with_normal_address(self):
        self.change_address("46 Everdean St.")
        self.compare_built_address("46 Everdean St Boston MA")
        
    def test_build_origin_address_with_malformed_address(self):
        self.change_address("foobar 46")
        self.compare_built_address("foobar Boston MA")

    def test_get_dest_addresses(self):
        data = get_test_data("#", PARKING_LOTS_TEST_DATA)
        to_test =  location_utils._get_dest_addresses(PARKING_LOTS_ADDR_INDEX, 
                                                      data[0:5])
        for address in to_test:
            self.assertTrue(address.find("Boston, MA"))

    def test_setup_google_maps_query_params(self):
        origin = "46 Everdean St Boston, MA"
        dests = ["123 Fake St Boston, MA", "1600 Penn Ave Washington, DC"]
        to_test = location_utils._setup_google_maps_query_params(origin, dests)
        self.assertEqual(origin, to_test["origins"])
        self.assertEqual(dests, to_test["destinations"].split("|"))
        self.assertEqual("imperial", to_test["units"])
