import intents.intent_constants
import intents.location_utils
import test.test_constants
import test.test_location_utils as tlu

import unittest

def suite():
    test_suite = unittest.TestLoader().loadTestsFromTestCase(tlu.LocationUtilsTestCase)
    return test_suite

if __name__ == "__main__":
    test_suite = suite()
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
