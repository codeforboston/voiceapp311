import csv
from unittest import mock

from mycity.intents import snow_parking_intent
from mycity.test import test_constants
from mycity.test.integration_tests.intent_base_case import IntentBaseCase
from mycity.test.integration_tests.intent_test_mixins import (
    CardTitleTestMixIn,
    CorrectSpeechOutputTestMixIn,
    RepromptTextTestMixIn,
)


##########################################
# TestCase class for snow_parking_intent #
##########################################

class SnowEmergencyTestCase(RepromptTextTestMixIn,
                            CardTitleTestMixIn,
                            CorrectSpeechOutputTestMixIn,
                            IntentBaseCase):
    intent_to_test = "SnowParkingIntent"
    expected_title = snow_parking_intent.SNOW_PARKING_CARD_TITLE
    returns_reprompt_text = False
    expected_card_title = snow_parking_intent.SNOW_PARKING_CARD_TITLE

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
            'mycity.intents.snow_parking_intent.FinderCSV.file_to_filtered_records',
            return_value=mock_filtered_record_return
        )

        mock_geocoded_address_candidates = test_constants.GEOCODE_ADDRESS_CANDIDATES

        self.mock_address_candidates = mock.patch(
            'mycity.utilities.finder.finder.arcgis_utils.geocode_address_candidates',
            return_value=mock_geocoded_address_candidates
        )

        mock_api_access_token = test_constants.ARCGIS_API_ACCESS_TOKEN

        self.mock_api_access_token = mock.patch(
            'mycity.utilities.finder.finder.arcgis_utils.generate_access_token',
            return_value=mock_api_access_token
        )

        mock_closest_destination = test_constants.ARCGIS_CLOSEST_DESTINATION
        self.mock_closest_destination = mock.patch(
            'mycity.utilities.finder.finder.arcgis_utils.find_closest_route',
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
