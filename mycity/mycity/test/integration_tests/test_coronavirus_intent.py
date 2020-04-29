import unittest
from mycity.mycity_request_data_model import MyCityRequestDataModel
import mycity.intents.coronavirus_update_intent as coronavirus_update_intent
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.integration_tests.intent_test_mixins as mix_ins

########################################
# TestCase class for CoronavirusIntent #
########################################


class CoronavirusIntentTestCase(base_case.IntentBaseCase,
                                mix_ins.CardTitleTestMixIn,
                                mix_ins.RepromptTextTestMixIn):

    intent_to_test = "CoronavirusUpdateIntent"
    expected_title = coronavirus_update_intent.INTENT_CARD_TITLE
    returns_reprompt_text = False

    def test_returns_session_attributes(self):
        mycity_request = MyCityRequestDataModel()
        mycity_request.session_attributes["test_key"] = "test_value"
        mycity_response = coronavirus_update_intent.get_coronovirus_update(
            mycity_request)
        self.assertEqual(
            "test_value", mycity_response.session_attributes["test_key"])

    def test_returns_valid_text(self):
        mycity_request = MyCityRequestDataModel()
        mycity_reponse = coronavirus_update_intent.get_coronovirus_update(
            mycity_request)
        self.assertFalse(
            coronavirus_update_intent.NO_UPDATE_ERROR in mycity_reponse.output_speech)
