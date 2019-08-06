import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.intents.food_truck_intent as food_truck_intent
import mycity.intents.intent_constants as intent_constants

import unittest

###################################
# TestCase class for trash_intent #
###################################

class FoodTruckTestCase(mix_ins.RepromptTextTestMixIn,
                        mix_ins.CardTitleTestMixIn,
                        mix_ins.CorrectSpeechOutputTestMixIn,
                        base_case.IntentBaseCase):

    intent_to_test = "FoodTruckIntent"
    expected_title = food_truck_intent.CARD_TITLE
    returns_reprompt_text = False
    expected_card_title = food_truck_intent.CARD_TITLE

    def setUp(self):
        """
        Patching out the functions in FoodTruckIntent that use requests.get
        """
        super().setUp()
        self.get_address_api_patch = \
            mock.patch('mycity.intents.trash_intent.get_address_api_info',
                       return_value=test_constants.GET_ADDRESS_API_MOCK)
        self.get_truck_locations_patch = \
            mock.patch('mycity.intents.trash_intent.get_trash_day_data',
                       return_value=test_constants.GET_FOOD_TRUCKS_MOCK)
        self.get_address_api_patch.start()
        self.get_truck_locations_patch.start()

    def tearDown(self):
        super().tearDown()
        self.get_address_api_patch.stop()
        self.get_truck_locations_patch.stop()

    def test_delegates_if_address_not_provided_no_geolocation_support(self):
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        response = self.controller.on_intent(self.request)
        self.assertEqual(response.dialog_directive['type'], "Dialog.Delegate")

    def test_requests_geolocation_permissions_if_device_capable(self):
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = False
        response = self.controller.on_intent(self.request)
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    def test_properly_uses_geolocation(self):
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = True
        self.request.geolocation_coordinates = {
            "latitudeInDegrees": 42.316466,
            "longitudeInDegrees": -71.056769,
        }
        response = self.controller.on_intent(self.request)
        self.assertNotEqual(response.card_type, "AskForPermissionsConsent")
        self.assertTrue(response.dialog_directive is None)


if __name__ == '__main__':
    unittest.main()