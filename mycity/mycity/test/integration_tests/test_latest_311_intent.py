from unittest import mock

from mycity.intents.speech_constants import latest_311_constants as intent_constants
from mycity.test.integration_tests.intent_base_case import IntentBaseCase
from mycity.test.integration_tests.intent_test_mixins import (
    CardTitleTestMixIn,
    CorrectSpeechOutputTestMixIn,
    RepromptTextTestMixIn,
)
from mycity.test.test_data import latest_311_fake_data


class Latest311TestCase(RepromptTextTestMixIn,
                        CardTitleTestMixIn,
                        CorrectSpeechOutputTestMixIn,
                        IntentBaseCase):

    intent_to_test = "LatestThreeOneOne"
    expected_title = intent_constants.REQUEST_311_CARD_TITLE
    returns_reprompt_text = False
    expected_card_title = intent_constants.REQUEST_311_CARD_TITLE

    def setUp(self):
        """
        Set up unit tests by mocking calls to 311
        """
        super().setUp()
        self.mock_311_service = mock.patch(
            'mycity.intents.latest_311_intent.get_raw_311_reports_json',
            return_value=latest_311_fake_data.FAKE_JSON_RESPONSE_3).start()

    def tearDown(self):
        """
        Stop mocked objects
        """
        super().tearDown()
        self.mock_311_service.stop()

    def test_slot_determines_number_of_reports(self):
        num_reports = 1
        self.request.intent_variables = \
            {
                intent_constants.REQUEST_311_NUMBER_REPORTS_SLOT_NAME:
                    {"value": num_reports}
            }
        self.mock_311_service.return_value = latest_311_fake_data.FAKE_JSON_RESPONSE_1
        response = self.controller.on_intent(self.request)
        self.mock_311_service.assert_called_once_with(num_reports)
        self.assertTrue(latest_311_fake_data.FAKE_LOCATION_1 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_TYPE_1 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_SUBJECT_1 in response.output_speech)

    def test_speech_can_contain_multiple_reports(self):
        num_reports = 3
        self.request.intent_variables = \
            {
                intent_constants.REQUEST_311_NUMBER_REPORTS_SLOT_NAME:
                    {"value": num_reports}
            }
        self.mock_311_service.return_value = latest_311_fake_data.FAKE_JSON_RESPONSE_3
        response = self.controller.on_intent(self.request)
        self.mock_311_service.assert_called_once_with(num_reports)

        # Data group 1
        self.assertTrue(latest_311_fake_data.FAKE_LOCATION_1 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_TYPE_1 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_SUBJECT_1 in response.output_speech)

        # Data group 1
        self.assertTrue(latest_311_fake_data.FAKE_LOCATION_2 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_TYPE_2 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_SUBJECT_2 in response.output_speech)

        # Data group 1
        self.assertTrue(latest_311_fake_data.FAKE_LOCATION_3 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_TYPE_3 in response.output_speech)
        self.assertTrue(latest_311_fake_data.FAKE_SUBJECT_3 in response.output_speech)
