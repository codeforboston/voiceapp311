from unittest import mock

from mycity.intents import get_alerts_intent as get_alerts
from mycity.intents.speech_constants import (
    get_alerts_intent as get_alerts_speech_constants,
)
from mycity.test import test_constants
from mycity.test.integration_tests import (
    intent_base_case as base_case,
    intent_test_mixins as mix_ins,
)

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
    some_alerts = test_constants.GET_ALERTS_MOCK_SOME_ALERTS

    """
    Patching get_alerts for right now since it seems too much of a hurdle to
    mock out requests and BeautifulSoup
    """

    def setUp(self):
        super().setUp()
        self.mock_get_alerts = \
            mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                       return_value=self.no_alerts.copy())
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
        self.assertEqual(response.output_speech, expected_response)

    @mock.patch('mycity.intents.get_alerts_intent.get_alerts',
                return_value=some_alerts.copy())
    def test_response_with_alerts(self, mock_get_alerts):
        response = self.controller.on_intent(self.request)
        self.assertIn('Godzilla inbound!', response.output_speech)
