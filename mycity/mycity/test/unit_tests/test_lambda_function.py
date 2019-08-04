""" Tests for functions specific to Alexa devices """

import lambda_function as lambda_function

import json
import unittest

class TestAlexaLambdaFunction(unittest.TestCase):

    def setUp(self):
        try:
            with open('mycity/test/test_data/base_alexa_request.json') as fh:
                self.alexa_request_json = json.load(fh)

        except Exception:
            print("Failed to read base Alexa request test data\n")
            pass

    def test_correct_mycity_conversion_for_no_geolocation_support(self):
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertFalse(mycity_request.device_has_geolocation)

    def test_correct_mycity_conversion_for_geolocation_support(self):
        self.alexa_request_json["context"]["System"]["device"] = {
            "supportedInterfaces" : {
                "Geolocation": {}
            }
        }
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertTrue(mycity_request.device_has_geolocation)


if __name__ == '__main__':
    unittest.main()