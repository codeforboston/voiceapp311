import unittest

import mycity.test.test_location_utils as loc_utils
import mycity.test.test_snow_emergency_parking as snow_parking
import mycity.test.test_open_spaces as open_spaces
import mycity.test.test_trash_intent as trash_intent
import mycity.test.test_unhandled_intent as unhandled_intent
import mycity.test.test_get_alerts as get_alerts
import mycity.test.test_mycity_controller as my_controller

# add test case to list
# TEST_CASES = [snow_parking.SnowEmergencyTestCase,
#               open_spaces.GetOpenSpacesTestCase,
#               trash_intent.TrashDayTestCase,
#               loc_utils.LocationUtilsTestCase,
#               unhandled_intent.UnhandledIntentTestCase,
#               get_alerts.GetAlertsTestCase
#               ]



TEST_CASES = [ my_controller.MyCityControllerUnitTestCase,
               loc_utils.LocationUtilsTestCase, # these testcases need mocked
                                                # requests for googlemaps,
                                                # featureservers, and other web
                                                # resources
               open_spaces.GetOpenSpacesTestCase,
               snow_parking.SnowEmergencyTestCase,
               get_alerts.GetAlertsTestCase,
               trash_intent.TrashDayTestCase


def load_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for test_case in TEST_CASES:
        suite.addTests(loader.loadTestsFromTestCase(test_case))
    return suite

if __name__ == "__main__":
    test_suite = load_tests()
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
