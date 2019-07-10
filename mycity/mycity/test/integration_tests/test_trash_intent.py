from unittest import mock

from mycity.intents import trash_intent
from mycity.test import test_constants
from mycity.test.integration_tests import (
    intent_base_case as base_case,
    intent_test_mixins as mix_ins,
)

###################################
# TestCase class for trash_intent #
###################################

class TrashDayTestCase(mix_ins.RepromptTextTestMixIn,
                       mix_ins.CardTitleTestMixIn,
                       mix_ins.CorrectSpeechOutputTestMixIn,
                       base_case.IntentBaseCase):
    intent_to_test = "TrashDayIntent"
    expected_title = trash_intent.CARD_TITLE
    returns_reprompt_text = False
    expected_card_title = trash_intent.CARD_TITLE

    def setUp(self):
        """
        Patching out the functions in TrashDayIntent that use requests.get
        """
        super().setUp()
        self.get_address_api_patch = \
            mock.patch('mycity.intents.trash_intent.get_address_api_info',
                       return_value=test_constants.GET_ADDRESS_API_MOCK)
        self.get_trash_day_data_patch = \
            mock.patch('mycity.intents.trash_intent.get_trash_day_data',
                       return_value=test_constants.GET_TRASH_DAY_MOCK)
        self.get_address_api_patch.start()
        self.get_trash_day_data_patch.start()

    def tearDown(self):
        super().tearDown()
        self.get_address_api_patch.stop()
        self.get_trash_day_data_patch.stop()
