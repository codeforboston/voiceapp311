import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.integration_tests.intent_test_mixins as mix_ins


############################################
# TestCase class for crime_incident_intent #
############################################

class CrimeIncidentsTestCase(mix_ins.RepromptTextTestMixIn,
                             mix_ins.CardTitleTestMixIn,
                             mix_ins.CorrectSpeechOutputTestMixIn,
                             base_case.IntentBaseCase):

    intent_to_test = "CrimeIncidentsIntent"
    expected_title = "CrimeIncidentsIntent"
    returns_reprompt_text = False

    def setUp(self):
        """
        Patching out the functions in CrimeIncidentsIntent that use requests.get
        """
        super().setUp()
        self.get_crime_incident_response = \
            mock.patch(
                ('mycity.intents.crime_activity_intent.'
                 'get_crime_incident_response'),
                return_value = test_constants.GET_CRIME_INCIDENTS_API_MOCK)
        self.get_crime_incident_response.start()

    def tearDown(self):
        super().tearDown()
        self.get_crime_incident_response.stop()
