"""
unit test for MyCityController 

"""

import unittest
import unittest.mock as mock

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_controller as mycity_con
import mycity.mycity_request_data_model as mycity_req
import mycity.mycity_response_data_model as mycity_res

class MyCityControllerUnitTestCase(unittest.TestCase):
    """
    testing:
        session started
        execute_request
        on_session_started
        on_launch
        on_intent
        on_session_ended
        get_welcome_response
        handle_session_end_request

    """

    def setUp(self):
        self.controller = mycity_con.MyCityController()
        self.request = mycity_req.MyCityRequestDataModel()

    def tearDown(self):
        self.controller = None

    @mock.patch('mycity.mycity_controller.print', create=True)
    def test_on_session_started_called_at_new_session(self, mock_print):
        self.request.is_new_session = True
        self.controller.execute_request(self.request)
        mock_print.assert_called_with(mycity_con.MyCityController.LOG_CLASS,
                                      '[method: on_session_started]',
                                      '[requestId: ' + str(self.request.request_id) + ']',
                                      '[sessionId: ' + str(self.request.session_id) + ']')
    
    def test_on_launch(self):
        self.request.is_new_session = False
        expected_session_attributes = self.request.session_attributes
        expected_output_speech = ("Welcome to the Boston Public Services skill. "
                                  "How can I help you? ")
        expected_reprompt_text = ("For example, you can tell me your address by "
                                  "saying, \"my address is\" followed by your "
                                  "address.")
        expected_card_title = "Welcome"
        response = self.controller.on_launch(self.request)
        self.assertEqual(response.session_attributes, expected_session_attributes)
        self.assertEqual(response.output_speech, expected_output_speech)
        self.assertEqual(response.reprompt_text, expected_reprompt_text)
        self.assertFalse(response.should_end_session)
    
    def test_execute_request_with_no_request_type(self):
        self.request.is_new_session = False
        self.request.request_type = None
        response = self.controller.execute_request(self.request)
        self.assertIsNone(response)

    def test_session_end_request(self):
        self.request.is_new_session = False
        self.request.request_type == "SessionEndedRequest"
        response = self.controller.execute_request(self.request)
        self.assertEqual(response, mycity_res.MyCityResponseDataModel()) # empty response

    def test_on_intent_AMAZON_StopIntent(self):
        expected_attributes = self.request.session_attributes
        expected_output_speech = ("Thank you for using the Boston Public "
                                  "Services skill. See you next time!")
        expected_card_title = "Boston Public Services - Thanks"
        self.request.intent_name = "AMAZON.StopIntent"
        response = self.controller.on_intent(self.request)
        self.assertEqual(response.session_attributes, expected_attributes)
        self.assertEqual(response.output_speech, expected_output_speech)
        self.assertEqual(response.card_title, expected_card_title)
        self.assertIsNone(response.reprompt_text)

    # if we change how we import intents in mycity_controller I think it will
    # break these patches
    @mock.patch('mycity.mycity_controller.set_address_in_session')
    def test_set_address_intent_no_address_prompted(self, mock_set_address):
        self.request.is_new_session = False
        self.request.intent_name = "SetAddressIntent"
        self.controller.on_intent(self.request)
        mock_set_address.assert_called_with(self.request)
     
    @mock.patch('mycity.mycity_controller.get_trash_day_info')
    def test_set_address_intent_prompted_from_another_intent(self, mock_trash_day):
        self.request.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT] = \
            "TrashDayIntent"
        self.request.intent_name = "SetAddressIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "46 Everdean St"
        self.controller.on_intent(self.request)
        # should call this intent after setting address
        mock_trash_day.assert_called_with(self.request)
   
    @mock.patch('mycity.mycity_controller.get_address_from_session')
    def test_set_address_intent_no_address_in_session_attributes(self, mock_get_addr):
        self.request.intent_name = "SetAddressIntent"
        self.controller.on_intent(self.request)
        mock_get_addr.assert_called_with(self.request)

    @mock.patch('mycity.mycity_controller.get_open_spaces_intent')
    def test_intent_that_needs_address_with_address_in_session_attributes(self, mock_intent):
        self.request.intent_name = "GetOpenSpacesIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "46 Everdean St"
        self.controller.on_intent(self.request)
        mock_intent.assert_called_with(self.request)

    @mock.patch('mycity.mycity_controller.request_user_address_response')
    def test_intent_that_needs_address_without_address_in_session_attributes(self, mock_intent):
        self.request.intent_name = "TrashDayIntent"
        self.controller.on_intent(self.request)
        mock_intent.assert_called_with(self.request)

    def test_unknown_intent(self):
        self.request.intent_name = "MadeUpIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = '46 Everdean St'
        with self.assertRaises(ValueError):
            self.controller.on_intent(self.request)
        
  


