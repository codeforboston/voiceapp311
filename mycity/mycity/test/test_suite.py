import unittest

from test_location_utils import LocationUtilsTestCase


def suite():
    test_suite = unittest.TestLoader().loadTestsFromTestCase(LocationUtilsTestCase)
    return test_suite


if __name__ == "__main__":
    test_suite = suite()
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
