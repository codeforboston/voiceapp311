"""
unit test for MyCityController 

"""

import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.mycity_controller as my_con
import mycity.intents.intent_constants as intent_constants
import mycity.test.unit_tests.base as base


class MyCityControllerUnitTestCase(base.BaseTestCase):
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

    def test_on_launch(self):
        self.request.is_new_session = False
        expected_session_attributes = self.request.session_attributes
        expected_output_speech = (
            "Welcome to the Boston Public Services skill. "
            "How can I help you? "
        )
        expected_reprompt_text = (
            "For example, you can tell me your address by saying, "
            "\"my address is\" followed by your address."
        )
        expected_card_title = "Welcome"
        response = self.controller.on_launch(self.request)
        self.assertEqual(
            response.session_attributes,
            expected_session_attributes
        )
        self.assertEqual(response.output_speech, expected_output_speech)
        self.assertEqual(response.reprompt_text, expected_reprompt_text)
        self.assertFalse(response.should_end_session)
    
    def test_execute_request_with_no_request_type(self):
        self.request.is_new_session = False
        self.request.request_type = None
        response = self.controller.execute_request(self.request)
        self.assertIsNone(response)

    def test_on_intent_AMAZON_StopIntent(self):
        expected_attributes = self.request.session_attributes
        expected_output_speech = (
            "Thank you for using the Boston Public Services skill. "
            "See you next time!"
        )
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
   
    @mock.patch('mycity.mycity_controller.get_address_from_session')
    def test_set_address_intent_no_address_in_session_attributes(
            self,
            mock_get_addr
    ):
        self.request.intent_name = "SetAddressIntent"
        self.controller.on_intent(self.request)
        mock_get_addr.assert_called_with(self.request)

    @mock.patch('mycity.mycity_controller.get_trash_day_info')
    def test_intent_that_needs_address_with_address_in_session_attributes(
            self,
            mock_intent
    ):
        self.request.intent_name = "TrashDayIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "46 Everdean St"
        self.controller.on_intent(self.request)
        mock_intent.assert_called_with(self.request)

    @mock.patch('mycity.mycity_controller.request_user_address_response')
    def test_intent_that_needs_address_without_address_in_session_attributes(
            self,
            mock_intent
    ):
        self.request.intent_name = "TrashDayIntent"
        self.controller.on_intent(self.request)
        mock_intent.assert_called_with(self.request)

    @mock.patch('requests.get')
    def test_get_address_from_user_device(self, mock_get):
        mock_resp = self._mock_response(status=200, 
            json_data=test_constants.ALEXA_DEVICE_ADDRESS)
        mock_get.return_value = mock_resp
        expected_output_text = "866 Huntington ave"
        result = self.controller.get_address_from_user_device(self.request)
        self.assertEquals(expected_output_text, 
            result.session_attributes[intent_constants.CURRENT_ADDRESS_KEY])

    @mock.patch('requests.get')
    def test_get_address_from_user_device_failure(self, mock_get):
        mock_resp = self._mock_response(status=403)
        mock_get.return_value = mock_resp
        expected_output = {}
        result = self.controller.get_address_from_user_device(self.request)
        self.assertEquals(expected_output, 
            result.session_attributes)

    def test_unknown_intent(self):
        self.request.intent_name = "MadeUpIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = '46 Everdean St'
        with self.assertRaises(ValueError):
            self.controller.on_intent(self.request)
