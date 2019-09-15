""" Tests utilities for location services  """

from mycity.mycity_request_data_model import MyCityRequestDataModel
import mycity.intents.intent_constants as intent_constants
import mycity.test.unit_tests.base as base
import mycity.utilities.location_services_utils as location_services_utils

import unittest

class LocationServicesUtilsUnitTestCase(base.BaseTestCase):

    def test_request_geolocation_permissions_card_type(self):
        response = location_services_utils.request_geolocation_permission_response()
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    def test_request_geolocation_permissions_card_permissions(self):
        response = location_services_utils.request_geolocation_permission_response()
        self.assertTrue(any("geolocation:read" in permission for permission in response.card_permissions))

    def test_boston_address_string_is_valid(self):
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "100 Main Street Boston MA"
        self.assertTrue(location_services_utils.is_current_address_in_city(request, "Boston"))

    def test_non_boston_address_string_is_not_valid(self):
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "100 Main Street New York NY"
        self.assertFalse(location_services_utils.is_current_address_in_city(request, "Boston"))

    def test_no_city_string_is_valid(self):
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "100 Main Street"
        self.assertTrue(location_services_utils.is_current_address_in_city(request, "Boston"))

    def test_zip_code_is_valid(self):
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "100 Main Street 02129"
        self.assertTrue(location_services_utils.is_current_address_in_city(request, "Boston"))       


if __name__ == '__main__':
    unittest.main()