""" Tests for functions specific to Alexa devices """

import lambda_function as lambda_function

import json
import unittest

class TestAlexaLambdaFunctionLocationServices(unittest.TestCase):

    def setUp(self):
        try:
            with open('mycity/test/test_data/base_alexa_request.json') as fh:
                self.alexa_request_json = json.load(fh)

        except Exception:
            print("Failed to read base Alexa request test data\n")
            pass

    def _add_geolocation_support_to_json(self):
        self.alexa_request_json["context"]["System"]["device"] = {
            "supportedInterfaces" : {
                "Geolocation": {}
            }
        }

    def _add_geolocation_info_to_json(self):
        self.alexa_request_json["context"]["Geolocation"] = {
             "coordinate": {
                "latitudeInDegrees": 38.2,
                "longitudeInDegrees": 28.3,
                "accuracyInMeters": 12.1 
            }
        }

    def test_correct_mycity_conversion_for_no_geolocation_support(self):
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertFalse(mycity_request.device_has_geolocation)

    def test_correct_mycity_conversion_for_geolocation_support(self):
        self._add_geolocation_support_to_json()
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertTrue(mycity_request.device_has_geolocation)

    def test_geolcation_no_oermission_on_unsupported_device(self):
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertFalse(mycity_request.geolocation_permission)

    def test_geolocation_no_permission_on_supported_device(self):
        self._add_geolocation_support_to_json()
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertFalse(mycity_request.geolocation_permission)

    def test_geolocation_permission_when_info_is_present(self):
        self._add_geolocation_support_to_json()
        self._add_geolocation_info_to_json()
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertTrue(mycity_request.geolocation_permission)

    def test_geolocation_permission_has_coordinates(self):
        self._add_geolocation_support_to_json()
        self._add_geolocation_info_to_json()
        mycity_request = lambda_function.platform_to_mycity_request(self.alexa_request_json)
        self.assertTrue("latitudeInDegrees" in mycity_request.geolocation_coordinates)
        self.assertTrue("longitudeInDegrees" in mycity_request.geolocation_coordinates)


if __name__ == '__main__':
    unittest.main()