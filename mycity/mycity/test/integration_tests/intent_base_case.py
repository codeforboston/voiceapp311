import unittest

from mycity import (
    mycity_controller as my_controller,
    mycity_request_data_model as req,
)
from mycity.intents import intent_constants

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
        self.controller = my_controller
        self.request = req.MyCityRequestDataModel()
        key = intent_constants.CURRENT_ADDRESS_KEY
        self.request._session_attributes[key] = "1000 Dorchester Ave"
        self.request.intent_name = self.intent_to_test

    def tearDown(self):
        self.controller = None
        self.request = None
