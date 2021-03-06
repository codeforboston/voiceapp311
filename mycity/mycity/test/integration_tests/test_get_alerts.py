import unittest.mock as mock
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.test_constants as test_constants
import mycity.intents.get_alerts_intent as get_alerts
import mycity.intents.speech_constants.get_alerts_intent as get_alerts_speech_constants


########################################
# TestCase class for get_alerts_intent #
########################################

class GetAlertsTestCase(mix_ins.RepromptTextTestMixIn,
                        mix_ins.CardTitleTestMixIn,
                        base_case.IntentBaseCase):

    intent_to_test = "GetAlertsIntent"
    expected_title = get_alerts.ALERTS_INTENT_CARD_TITLE
    returns_reprompt_text = False
    # if we don't create copies of these dictionaries we'll create empty
    # dictionary errors after successive setUps and tearDowns
    no_alerts = test_constants.GET_ALERTS_MOCK_NO_ALERTS
    one_alert = test_constants.GET_ALERTS_MOCK_ONE_ALERT
    some_alerts = test_constants.GET_ALERTS_MOCK_SOME_ALERTS

    """
    Patching get_alerts for right now since it seems too much of a hurdle to
    mock out requests and BeautifulSoup
    """

    def setUp(self):
        super().setUp()
        self.mock_get_alerts = \
            mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                       return_value = self.no_alerts.copy())
        self.mock_get_alerts.start()

    def tearDown(self):
        super().setUp()
        self.mock_get_alerts.stop()
        self.mock_get_alerts = None

    # these tests required patches to pass tests...not sure why
    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=no_alerts.copy())
    def test_response_with_no_alerts(self, mock_get_alerts):
        response = self.controller.on_intent(self.request)
        expected_response = get_alerts_speech_constants.NO_ALERTS
        self.assertTrue(response.should_end_session)
        self.assertEqual(response.output_speech, expected_response)

    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=one_alert.copy())
    def test_response_with_one_alert(self, mock_get_alerts):
        response = self.controller.on_intent(self.request)
        self.assertTrue(response.should_end_session)
        self.assertIn('Godzilla inbound!', response.output_speech)
        self.assertIsNone(response.dialog_directive)

    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=some_alerts.copy())
    def test_response_with_selected_alerts(self, mock_get_alerts):
        # first response
        response = self.controller.on_intent(self.request)
        alerts = response.session_attributes['alerts']
        self.assertFalse(response.should_end_session)
        self.assertIn('Godzilla inbound!', alerts.values())
        self.assertIn('5', response.output_speech)
        self.assertIsNotNone(response.dialog_directive)
        # second response for valid decision
        self.request.session_attributes = response.session_attributes
        self.request.intent_variables['ServiceName'] = {'value': 'alert header'}
        response = self.controller.on_intent(self.request)
        self.assertTrue(response.should_end_session)
        self.assertIn('Godzilla inbound!', response.output_speech)

    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=some_alerts.copy())
    def test_response_with_all_alerts(self, mock_get_alerts):
        # first response
        response = self.controller.on_intent(self.request)
        alerts = response.session_attributes['alerts']
        self.assertFalse(response.should_end_session)
        self.assertIn('Godzilla inbound!', alerts.values())
        self.assertIn('5', response.output_speech)
        self.assertIsNotNone(response.dialog_directive)
        # second 'all' response
        self.request.session_attributes = response.session_attributes
        self.request.intent_variables['ServiceName'] = {'value': 'all'}
        response = self.controller.on_intent(self.request)
        self.assertTrue(response.should_end_session)
        for alert in alerts.values():
            self.assertIn(alert, response.output_speech)

    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=some_alerts.copy())
    def test_response_invalid_decision(self, mock_get_alerts):
        # first response
        response = self.controller.on_intent(self.request)
        alerts = response.session_attributes['alerts']
        self.assertFalse(response.should_end_session)
        self.assertIn('Godzilla inbound!', alerts.values())
        self.assertIn('5', response.output_speech)
        self.assertIsNotNone(response.dialog_directive)
        # second invalid decision response
        self.request.session_attributes = response.session_attributes
        self.request.intent_variables['ServiceName'] = {'value': 'school closings'}
        response = self.controller.on_intent(self.request)
        alerts = response.session_attributes['alerts']
        self.assertFalse(response.should_end_session)
        self.assertIn("I didn't understand", response.output_speech)
        self.assertIn('Godzilla inbound!', alerts.values())
        self.assertIn('5', response.output_speech)
