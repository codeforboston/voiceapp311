import unittest

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_controller as mcc
import mycity.mycity_request_data_model as req
import mycity.test.test_constants as test_constants




###############################################################################
# TestCase parent class for all intent TestCases, which are integration tests #
# to see if any changes in codebase have broken response-request model.       #
#                                                                             #
# NOTE: Assumes that address has already been set.                            #
###############################################################################

class IntentBaseCase(unittest.TestCase):

    __test__ = False

    intent_to_test = None
    returns_reprompt_text = False

    @classmethod
    def setUpClass(cls):
        cls.controller = mcc.MyCityController()
        cls.request = req.MyCityRequestDataModel()
        key = intent_constants.CURRENT_ADDRESS_KEY
        cls.request._session_attributes[key] = "46 Everdean St"
        cls.request.intent_name = cls.intent_to_test
        cls.response = cls.controller.on_intent(cls.request)

    @classmethod
    def tearDownClass(cls):
        cls.controller = None
        cls.request = None

    def test_for_smoke(self):
        self.assertNotIn("Uh oh", self.response.output_speech)
        self.assertNotIn("Error", self.response.output_speech)

    def test_correct_intent_card_title(self):
        self.assertEqual(self.intent_to_test, self.response.card_title)


    @unittest.skipIf(not returns_reprompt_text, 
                     "{} shouldn't return a reprompt text".format(intent_to_test))
    def test_returning_reprompt_text(self):
        self.assertIsNotNone(self.response.reprompt_text)


    @unittest.skipIf(returns_reprompt_text,
                     "{} should return a reprompt text".format(intent_to_test))
    def test_returning_no_reprompt_text(self):
        self.assertIsNone(self.response.reprompt_text)
