from unittest import mock

from mycity.intents import crime_activity_intent as crime_intent
from mycity.test import test_constants
from mycity.test.integration_tests import (
    intent_base_case as base_case,
    intent_test_mixins as mix_ins,
)

############################################
# TestCase class for crime_incident_intent #
############################################

MOCK_RESPONSE = test_constants.GET_CRIME_INCIDENTS_API_MOCK
RESULT = crime_intent.RESULT_FIELD
RECORDS = crime_intent.RECORDS_FIELD
STREET = crime_intent.STREET_FIELD

class CrimeIncidentsTestCase(mix_ins.RepromptTextTestMixIn,
                             mix_ins.CardTitleTestMixIn,
                             base_case.IntentBaseCase):

    intent_to_test = "CrimeIncidentsIntent"
    expected_title = crime_intent.CARD_TITLE_CRIME
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
                return_value=test_constants.GET_CRIME_INCIDENTS_API_MOCK)
        self.get_crime_incident_response.start()
        response = self.controller.on_intent(self.request)
        for record in MOCK_RESPONSE[RESULT][RECORDS]:
            self.assertIn(record[STREET], response.output_speech)

    def tearDown(self):
        super().tearDown()
        self.get_crime_incident_response.stop()
