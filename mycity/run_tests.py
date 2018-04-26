import mycity.intents.intent_constants
import mycity.intents.location_utils
import mycity.test.test_constants
from mycity.test.test_location_utils import LocationUtilsTestCase
from mycity.test.test_snow_emergency_parking import SnowEmergencyTestCase
import unittest


tests = [LocationUtilsTestCase,
         SnowEmergencyTestCase]

def load_tests(tests):
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test))
    return suite

if __name__ == "__main__":
    test_suite = load_tests(tests)
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
