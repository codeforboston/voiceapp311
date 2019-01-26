import mycity.intents.intent_constants as intent_constants
import mycity.test.unit_tests.base as base
import mycity.intents.get_alerts_intent as get_alerts_intent
import mycity.intents.speech_constants.get_alerts_intent as constants
import typing


class GetAlertsIntentTestCase(base.BaseTestCase):

    get_alerts_stub_return_dictionary = {}
    prune_normal_responses_return_dictionary = {}
    alerts_to_speech_return_string = ''

    def setUp(self):
        super(GetAlertsIntentTestCase, self).setUp()

    def tearDown(self):
        super(GetAlertsIntentTestCase, self).tearDown()
        self.get_alerts_stub_return_dictionary = {}
        self.prune_normal_responses_return_dictionary = {}
        self.alerts_to_speech_return_string = ''

    def stub_prune_normal_responses(self, *args) -> typing.Dict:
        return self.prune_normal_responses_return_dictionary

    def stub_get_alerts(self, *args) -> typing.Dict:
        return self.get_alerts_stub_return_dictionary

    def stub_alerts_to_speech(self, *args) -> typing.AnyStr:
        return self.alerts_to_speech_return_string

    def test_that_get_alerts_intent_will_not_end_session(self):
        response = get_alerts_intent.get_alerts_intent(
            self.request,
            self.stub_get_alerts,
            self.stub_prune_normal_responses,
            self.stub_alerts_to_speech
        )
        self.assertFalse(response.should_end_session)

    def test_that_get_alerts_intent_sets_reponse_output_speech_with_return_value_of_alerts_to_speech(self):
        output_speech = 'Bingo'
        self.alerts_to_speech_return_string = output_speech
        response = get_alerts_intent.get_alerts_intent(
            self.request,
            self.stub_get_alerts,
            self.stub_prune_normal_responses,
            self.stub_alerts_to_speech
        )
        self.assertEquals(output_speech, response.output_speech)

    def test_that_alerts_to_speech_output_concats_values_of_alert_dictionary_into_string(self):
        expected = 'This is a test. Big test.'
        alerts = dict()
        alerts[get_alerts_intent.Services.TRASH.value] = 'This is a test.'
        alerts[get_alerts_intent.Services.SCHOOLS.value] = 'Big test.'
        self.assertEquals(expected, get_alerts_intent.alerts_to_speech_output(alerts))

    def test_that_alerts_to_speech_output_returns_default_response_if_no_alerts_in_dictionary(self):
        expected = constants.NO_ALERTS
        alerts = dict()
        self.assertEquals(expected, get_alerts_intent.alerts_to_speech_output(alerts))

    def test_that_prune_normal_responses_returns_an_empty_dictionary_if_all_responses_are_normal(self):
        alerts = dict()
        alerts[get_alerts_intent.Services.SCHOOLS.value] = 'Very normal!'
        alerts[get_alerts_intent.Services.TRASH.value] = 'Too normal in my opinion'
        alerts[get_alerts_intent.Services.TOW_LOT.value] = get_alerts_intent.TOW_LOT_NORMAL_MESSAGE
        self.assertEqual({}, get_alerts_intent.prune_normal_responses(alerts))

    def test_inclement_weather_alert_returns_normal_response_for_no_alert(self):
        response = get_alerts_intent.get_inclement_weather_alert(
            self.request,
            self.stub_get_alerts)
        self.assertEqual(constants.NO_INCLEMENT_WEATHER_ALERTS, response.output_speech)

    def test_inclement_weather_alert_returns_normal_response_for_keyword_in_wrong_alert_section(self):
        self.get_alerts_stub_return_dictionary = {
            get_alerts_intent.Services.PARKING_METERS: "Snow doesn't bother us!"
        }
        response = get_alerts_intent.get_inclement_weather_alert(
            self.request,
            self.stub_get_alerts)
        self.assertEqual(constants.NO_INCLEMENT_WEATHER_ALERTS, response.output_speech)

    def test_inclement_weather_alert_returns_alerts_when_snow_in_alert_banner(self):
        snow_emergency_alert = "It's a snow emergency!"
        self.get_alerts_stub_return_dictionary = {
            get_alerts_intent.Services.ALERT_HEADER.value: snow_emergency_alert
        }
        response = get_alerts_intent.get_inclement_weather_alert(
            self.request,
            self.stub_get_alerts)
        self.assertEqual(snow_emergency_alert, response.output_speech)

    def test_inclement_weather_alert_returns_normal_when_other_notice_in_alert_banner(self):
        snow_emergency_alert = "Patriots win the super bowl!"
        self.get_alerts_stub_return_dictionary = {
            get_alerts_intent.Services.ALERT_HEADER.value: snow_emergency_alert
        }
        response = get_alerts_intent.get_inclement_weather_alert(
            self.request,
            self.stub_get_alerts)
        self.assertEqual(constants.NO_INCLEMENT_WEATHER_ALERTS, response.output_speech)
