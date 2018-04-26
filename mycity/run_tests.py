import mycity.intents.intent_constants
import mycity.intents.location_utils
import mycity.test.test_constants
from mycity.test.test_location_utils import LocationUtilsTestCase
from mycity.test.test_snow_emergency_parking import SnowEmergencyTestCase
from mycity.test.test_open_spaces import GetOpenSpacesTestCase
import unittest


##################################################################################
# Functions that are used by intents by are not intents per se. You will have to #
# write unittests for these explicitly                                           #
##################################################################################

utilities_to_test = [LocationUtilsTestCase]

intents_to_test = [SnowEmergencyTestCase, GetOpenSpacesTestCase]

def load_tests(utilities_to_test, intents_to_test):
    suite = unittest.TestSuite()
    for utility in utilities_to_test:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(utility))
    for intent in intents_to_test:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(intent))
    return suite

if __name__ == "__main__":
    test_suite = load_tests(utilities_to_test, intents_to_test)
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
