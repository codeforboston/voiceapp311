import unittest
import unittest.mock as mock

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_controller as my_controller
import mycity.mycity_request_data_model as req
import mycity.test.test_constants as test_constants




###############################################################################
# TestCase parent class for all intent TestCases, which are integration tests #
# to see if any changes in codebase have broken response-request model.       #
#                                                                             #
# NOTE: Assumes that address has already been set.                            #
###############################################################################

class IntentBaseCase(unittest.TestCase):

    intent_to_test = None
    returns_reprompt_text = False

    def setUp(self):
        self.controller = mcc
        self.request = req.MyCityRequestDataModel()
        key = intent_constants.CURRENT_ADDRESS_KEY
        self.request._session_attributes[key] = "1000 Dorchester Ave"
        self.request.intent_name = self.intent_to_test

    def tearDown(self):
        self.controller = None
        self.request = None

