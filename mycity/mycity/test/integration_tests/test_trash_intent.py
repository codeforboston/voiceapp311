import json
import unittest.mock as mock

import mycity.test.test_constants as test_constants
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.integration_tests.intent_test_mixins as mix_ins



###################################
# TestCase class for trash_intent #
###################################

class TrashDayTestCase(mix_ins.IntentRepromptTextTestMixIn,
                       mix_ins.IntentCardTitleTestMixIn,
                       mix_ins.IntentTestForErrorMixIn,
                       base_case.IntentBaseCase):


    intent_to_test = "TrashDayIntent"
    returns_reprompt_text = False

    def setUp(self):
        """
        Patching out the functions in TrashDayIntent that use requests.get
        """
        super().setUp()
        self.get_address_api_patch = \
            mock.patch('mycity.intents.trash_intent.get_address_api_info',
                       return_value = test_constants.GET_ADDRESS_API_MOCK)
        self.get_trash_day_data_patch = \
            mock.patch('mycity.intents.trash_intent.get_trash_day_data',
                       return_value = test_constants.GET_TRASH_DAY_MOCK)
        self.get_address_api_patch.start()
        self.get_trash_day_data_patch.start()
 
    def tearDown(self):
        super().tearDown()
        self.get_address_api_patch.stop()
        self.get_trash_day_data_patch.stop()

