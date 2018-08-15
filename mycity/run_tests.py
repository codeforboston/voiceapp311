import unittest
import argparse

import mycity.test.integration_tests.test_snow_emergency_parking as snow_parking
import mycity.test.integration_tests.test_trash_intent as trash_intent
import mycity.test.integration_tests.test_unhandled_intent as unhandled_intent
import mycity.test.integration_tests.test_get_alerts as get_alerts
import mycity.test.unit_tests.test_finder_csv as finder_csv
import mycity.test.unit_tests.test_mycity_controller as my_controller
import mycity.test.unit_tests.test_address_utils as address_utils
import mycity.test.unit_tests.test_csv_utils as csv_utils
import mycity.test.unit_tests.test_gis_utils as gis_utils


TEST_CASES = [  my_controller.MyCityControllerUnitTestCase,
                address_utils.AddressUtilitiesTestCase,
                csv_utils.CSVUtilitiesTestCase,
                gis_utils.GISUtilitiesTestCase,
                finder_csv.FinderCSVTestCase,
                get_alerts.GetAlertsTestCase,
                trash_intent.TrashDayTestCase,
                unhandled_intent.UnhandledIntentTestCase,
                snow_parking.SnowEmergencyTestCase
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
