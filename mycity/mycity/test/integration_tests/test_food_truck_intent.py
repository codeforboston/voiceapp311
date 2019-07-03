from unittest import mock

from mycity.intents import food_truck_intent
from mycity.test import test_constants
from mycity.test.integration_tests import (
    intent_base_case as base_case,
    intent_test_mixins as mix_ins,
)


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
