"""
unit test for MyCityController 

"""

import unittest.mock as mock

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_controller as my_con
import mycity.test.test_constants as test_constants
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
        expected_output_speech = my_con.LAUNCH_SPEECH
        expected_reprompt_text = my_con.LAUNCH_REPROMPT_SPEECH
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
            "Thank you for using the Boston Info skill. "
            "See you next time!"
        )
        expected_card_title = "Boston Info - Thanks"
        self.request.intent_name = "AMAZON.StopIntent"
        response = self.controller.on_intent(self.request)
        self.assertEqual(response.session_attributes, expected_attributes)
        self.assertEqual(response.output_speech, expected_output_speech)
        self.assertEqual(response.card_title, expected_card_title)
        self.assertIsNone(response.reprompt_text)

    @mock.patch('mycity.mycity_controller.get_trash_day_info')
    def test_intent_that_needs_address_with_address_in_session_attributes(
            self,
            mock_intent
    ):
        self.request.intent_name = "TrashDayIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "46 Everdean St"
        self.controller.on_intent(self.request)
        mock_intent.assert_called_with(self.request)


    def test_unknown_intent(self):
        self.request.intent_name = "MadeUpIntent"
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = '46 Everdean St'
        with self.assertRaises(ValueError):
            self.controller.on_intent(self.request)
