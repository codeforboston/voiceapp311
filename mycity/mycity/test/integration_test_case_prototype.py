import mycity.intents.intent_constants as intent_constants
import mycity.intents.snow_parking_intent as snow_parking
import mycity.mycity_controller as mcc
import mycity.mycity_request_data_model as req
import mycity.test.test_constants as test_constants
import unittest
import unittest.mock as mock


###############################################################################
# TestCase parent class for all intent TestCases, which are integration tests #
# to see if any changes in codebase have broken response-request model.       #
#                                                                             #
# NOTE: Assumes that address has already been set.                            #
###############################################################################

class IntegrationTestCasePrototype(unittest.TestCase):

    def setUp(self):
        self.controller = mcc.MyCityController()
        self.request = req.MyCityRequestDataModel()
        key = intent_constants.CURRENT_ADDRESS_KEY
        self.request._session_attributes[key] = "46 Everdean St"
        self.intent_to_test = None
    
    def tearDown(self):
        self.controller = None
        self.request = None
