import unittest

import mycity.test.integration_tests.test_snow_emergency_parking as snow_parking
import mycity.test.integration_tests.test_trash_intent as trash_intent
import mycity.test.integration_tests.test_unhandled_intent as unhandled_intent
import mycity.test.integration_tests.test_get_alerts as get_alerts
import mycity.test.unit_tests.test_location_utils as loc_utils
import mycity.test.unit_tests.test_mycity_controller as my_controller


TEST_CASES = [ my_controller.MyCityControllerUnitTestCase,
               loc_utils.LocationUtilsTestCase,
               snow_parking.SnowEmergencyTestCase,
               get_alerts.GetAlertsTestCase,
               trash_intent.TrashDayTestCase,
               unhandled_intent.UnhandledIntentTestCase
               ]

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
