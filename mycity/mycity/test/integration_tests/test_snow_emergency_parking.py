import csv
import unittest.mock as mock
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.test_constants as test_constants
import mycity.intents.intent_constants as intent_constants
import mycity.intents.snow_parking_intent as snow_parking
from mycity.mycity_request_data_model import MyCityRequestDataModel

import unittest


##########################################
# TestCase class for snow_parking_intent #
##########################################

class SnowEmergencyTestCase(mix_ins.RepromptTextTestMixIn,
                            mix_ins.CardTitleTestMixIn,
                            mix_ins.CorrectSpeechOutputTestMixIn,
                            base_case.IntentBaseCase):

    intent_to_test = "SnowParkingIntent"
    expected_title = intent_constants.SNOW_PARKING_CARD_TITLE
    returns_reprompt_text = False
    expected_card_title = intent_constants.SNOW_PARKING_CARD_TITLE

    def setUp(self):
        """
        Set up the controller and request using superclass constructor.
        Then, patch the two functions in the intent that use web resources.
        """
        super().setUp()

        def fake_filter(record):
            return record

        self.csv_file = open(test_constants.PARKING_LOTS_TEST_CSV,
                             encoding='utf-8-sig')
        mock_filtered_record_return = list(filter(fake_filter,
                                                  csv.DictReader(
                                                      self.csv_file,
                                                      delimiter=','
                                                  )))
        self.mock_filtered_record = mock.patch(
            ('mycity.intents.snow_parking_intent.'
             'FinderCSV.file_to_filtered_records'),
            return_value=mock_filtered_record_return
        )

        mock_geocoded_address_candidates = \
                test_constants.GEOCODE_ADDRESS_CANDIDATES


        self.mock_address_candidates = \
            mock.patch(
                'mycity.utilities.finder.Finder.arcgis_utils.geocode_address_candidates',
                return_value=mock_geocoded_address_candidates
            )

        mock_api_access_token = \
                test_constants.ARCGIS_API_ACCESS_TOKEN

        self.mock_api_access_token = \
                mock.patch(
                    'mycity.utilities.finder.Finder.arcgis_utils.generate_access_token',
                    return_value=mock_api_access_token
                )

        mock_closest_destination = \
                test_constants.ARCGIS_CLOSEST_DESTINATION
        self.mock_closest_destination = \
                mock.patch(
                        'mycity.utilities.finder.Finder.arcgis_utils.find_closest_route',
                        return_value=mock_closest_destination
                    )



        self.mock_filtered_record.start()
        self.mock_address_candidates.start()
        self.mock_api_access_token.start()
        self.mock_closest_destination.start()

    def tearDown(self):
        super().tearDown()
        self.csv_file.close()
        self.mock_filtered_record.stop()
        self.mock_address_candidates.stop()
        self.mock_api_access_token.stop()
        self.mock_closest_destination.stop()

    def test_requests_geolocation_permissions_if_supported(self):
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = False
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    @mock.patch('mycity.intents.snow_parking_intent.location_services_utils.get_address_from_user_device')
    def test_requests_device_address_if_supported(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), False)
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = False
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual(response.card_type, "AskForPermissionsConsent")

    @mock.patch('mycity.intents.snow_parking_intent.location_services_utils.get_address_from_user_device')
    def test_fallback_to_manual_request_if_no_device_address(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), True)
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = False
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual("Address", response.card_title)

    def test_geolocation_finds_closest_parking(self):
        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = True
        self.request.geolocation_permission = True
        self.request.geolocation_coordinates = {
            "latitudeInDegrees": 42.316466,
            "longitudeInDegrees": -71.056769,
        }
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual(self.expected_card_title, response.card_title)

    @mock.patch('mycity.intents.snow_parking_intent.location_services_utils.get_address_from_user_device')
    def test_device_address_finds_closest_parking(self, mock_get_address):
        request_with_address = MyCityRequestDataModel()
        request_with_address._session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "1000 Dorchester Ave"
        mock_get_address.return_value = (request_with_address, True)

        self.request._session_attributes.pop(intent_constants.CURRENT_ADDRESS_KEY, None)
        self.request.device_has_geolocation = False
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual(self.expected_card_title, response.card_title)

    def test_parsed_address_not_in_boston(self):
        self.mock_address_candidates.return_value = test_constants.GEOCODE_OUTER_ADDRESS_CANDIDATES
        self.request._session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "1 Broadway, Cambridge"
        response = snow_parking.get_snow_emergency_parking_intent(self.request)
        self.assertEqual(response.output_speech, intent_constants.NOT_IN_BOSTON_SPEECH)
        # return to expected value
        self.mock_address_candidates.return_value = test_constants.GEOCODE_ADDRESS_CANDIDATES


if __name__ == '__main__':
    unittest.main()


