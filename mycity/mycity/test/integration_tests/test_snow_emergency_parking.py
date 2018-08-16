import csv
import unittest.mock as mock
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.test_constants as test_constants


##########################################
# TestCase class for snow_parking_intent #
##########################################

class SnowEmergencyTestCase(mix_ins.RepromptTextTestMixIn, 
                            mix_ins.CardTitleTestMixIn,
                            mix_ins.CorrectSpeechOutputTestMixIn,
                            base_case.IntentBaseCase):

    intent_to_test = "SnowParkingIntent"
    expected_title  = "Snow Parking"
    returns_reprompt_text = False
    expected_card_title = "Snow Parking"

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
        mock_get_driving_info_return = \
            test_constants.CLOSEST_PARKING_DRIVING_DATA
        self.get_driving_info_patch = \
            mock.patch(
                ('mycity.intents.snow_parking_intent.g_maps_utils'
                 '._get_driving_info'),
                return_value=mock_get_driving_info_return
            )
        self.mock_filtered_record.start()
        self.get_driving_info_patch.start()

    def tearDown(self):
        super().tearDown()
        self.csv_file.close()
        self.mock_filtered_record.stop()
        self.get_driving_info_patch.stop()


