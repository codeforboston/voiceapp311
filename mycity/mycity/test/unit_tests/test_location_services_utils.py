
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

if __name__ == '__main__':
    unittest.main()