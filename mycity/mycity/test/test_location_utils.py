import ast
import mycity.intents.intent_constants as intent_constants
import mycity.intents.location_utils as location_utils
import mycity.test.test_constants as test_constants
import unittest
import unittest.mock

# char that indicates that line in a data file is a comment
COMMENT_CHAR = "#"

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
    with open(filename, "r") as f:
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
        self.mcrd = unittest.mock.MagicMock() # mcrd ==> MyCityRequestDataModel
        self.mcrd.session_attributes = {}
        self.mcrd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = ""

    def change_address(self, new_address):
        self.mcrd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            new_address

    def compare_built_address(self, expected_result):
        origin_addr = location_utils.build_origin_address(self.mcrd)
        self.assertEqual(origin_addr, expected_result)
 
    def tearDown(self):
        self.mcrd = None

    def test_build_origin_address_with_normal_address(self):
        self.change_address("46 Everdean St.")
        self.compare_built_address("46 Everdean St Boston MA")
        
    def test_build_origin_address_with_malformed_address(self):
        self.change_address("foobar 46")
        self.compare_built_address("foobar Boston MA")

    def test_get_dest_addresses(self):
        data = get_test_data(COMMENT_CHAR, test_constants.PARKING_LOTS_TEST_DATA)
        to_test = \
            location_utils._get_dest_addresses(
            test_constants.PARKING_LOTS_ADDR_INDEX, 
            data[0:5]
            )
        for address in to_test:
            self.assertTrue(address.find("Boston, MA"))

    def test_get_closest_feature(self):
        data = get_test_data(COMMENT_CHAR, test_constants.PARKING_LOTS_TEST_DATA)

    def test_setup_google_maps_query_params(self):
        origin = "46 Everdean St Boston, MA"
        dests = ["123 Fake St Boston, MA", "1600 Penn Ave Washington, DC"]
        to_test = location_utils._setup_google_maps_query_params(origin, dests)
        self.assertEqual(origin, to_test["origins"])
        self.assertEqual(dests, to_test["destinations"].split("|"))
        self.assertEqual("imperial", to_test["units"])

    def test_parse_closest_location_info(self):
        feature_type = 'Fake feature'
        closest_location_info = {'Driving distance': 'fake',
                              'Driving distance text': 'also fake',
                              'Driving time': 'triply fake',
                              'Driving time text': 'fake like a mug',
                              feature_type: 'fake fake fake fake'}
        to_test = location_utils._parse_closest_location_info(feature_type, closest_location_info)
        self.assertIn(location_utils.DRIVING_DISTANCE_TEXT_KEY, to_test)
        self.assertIn(location_utils.DRIVING_TIME_TEXT_KEY, to_test)
        self.assertIn(feature_type, to_test)
        self.assertNotIn('Driving time', to_test)
        self.assertNotIn('Driving distance', to_test)
