import unittest

from mycity import mycity_controller
from mycity.intents import intent_constants
from mycity.mycity_request_data_model import MyCityRequestDataModel


###############################################################################
# TestCase parent class for all intent TestCases, which are integration tests #
# to see if any changes in codebase have broken response-request model.       #
#                                                                             #
# NOTE: Assumes that address has already been set.                            #
###############################################################################

class IntentBaseCase(unittest.TestCase):
    intent_to_test = None
    expected_title = 'Boston Info'
    returns_reprompt_text = False

    def setUp(self):
        self.controller = mycity_controller
        self.request = MyCityRequestDataModel()
        key = intent_constants.CURRENT_ADDRESS_KEY
        self.request._session_attributes[key] = "1000 Dorchester Ave"
        self.request.intent_name = self.intent_to_test

    def tearDown(self):
        self.controller = None
        self.request = None
