from mycity.mycity_request_data_model import MyCityRequestDataModel
import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.intents.crime_activity_intent as crime_intent
import mycity.intents.intent_constants as intent_constants
import unittest

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

    def test_requests_geolocation_permissions_if_supported(self):
        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = False
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    @mock.patch('mycity.intents.crime_activity_intent.get_address_from_user_device')
    def test_requests_device_address_if_supported(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), False)
        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = False
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    @mock.patch('mycity.intents.crime_activity_intent.get_address_from_user_device')
    def test_fallback_to_manual_request_if_no_device_address(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), True)
        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY, 
            None)
        self.request.device_has_geolocation = False
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual("Address", response.card_title)
    
    def test_geolocation_finds_closest_parking(self):
        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = True
        self.request.geolocation_coordinates = {
            "latitudeInDegrees": 42.316466,
            "longitudeInDegrees": -71.056769,
        }
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(self.expected_title, response.card_title)
        self.assertTrue(response.output_speech)
        self.assertNotEqual(response.output_speech, intent_constants.NOT_IN_BOSTON_SPEECH)

    @mock.patch('mycity.intents.crime_activity_intent.get_address_from_user_device')
    def test_device_address_finds_closest_parking(self, mock_get_address):
        request_with_address = MyCityRequestDataModel()
        request_with_address._session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY] = "1000 Dorchester Ave"
        mock_get_address.return_value = (request_with_address, True)

        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = False
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(self.expected_title, response.card_title)
        self.assertTrue(response.output_speech)
        self.assertNotEqual(response.output_speech, intent_constants.NOT_IN_BOSTON_SPEECH)

    @mock.patch('mycity.intents.crime_activity_intent.get_address_from_user_device')
    def test_device_address_not_in_boston(self, mock_get_address):
        request_with_address = MyCityRequestDataModel()
        request_with_address._session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY] = "795 Massachusetts Ave Cambridge MA"
        mock_get_address.return_value = (request_with_address, True)

        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = False
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(self.expected_title, response.card_title)
        self.assertEqual(response.output_speech, intent_constants.NOT_IN_BOSTON_SPEECH)

    def test_geolocation_not_in_boston(self):
        self.request._session_attributes.pop(
            intent_constants.CURRENT_ADDRESS_KEY,
            None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = True
        self.request.geolocation_coordinates = {
            "latitudeInDegrees": 42.367013,
            "longitudeInDegrees": -71.105786,
        }
        response = crime_intent.get_crime_incidents_intent(self.request)
        self.assertEqual(self.expected_title, response.card_title)
        self.assertTrue(response.output_speech)
        self.assertEqual(response.output_speech, intent_constants.NOT_IN_BOSTON_SPEECH)

if __name__ == '__main__':
    unittest.main()
