import unittest

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_controller as my_controller
import mycity.mycity_request_data_model as my_req


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = my_con
        self.request = my_req.MyCityRequestDataModel()
        
    def tearDown(self):
        self.controller = None
        self.request = None

        
