import csv
import unittest.mock as mock

import mycity.utilities.google_maps_utils as g_maps_utils
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
    returns_reprompt_text = False

    def setUp(self):
        """
        Set up the controller and request using superclass constructor.
        Then, patch the two functions in the intent that use web 
        resources

        """
        super().setUp()
        self.csv_file = open(test_constants.PARKING_LOTS_TEST_CSV, encoding = 'utf-8-sig')
        mock_parking_locations_return = csv.reader(self.csv_file, delimiter =',')
        mock_get_driving_info_return = {"Parking Lot": "111 Western Ave Boston, MA",
                                        g_maps_utils.DRIVING_DISTANCE_TEXT_KEY:
                                            "100 miles",
                                        g_maps_utils.DRIVING_TIME_TEXT_KEY:
                                            "15 minutes"}
        self.get_parking_location_patch = \
            mock.patch(('mycity.intents.snow_parking_intent.'
                        '_get_parking_locations'),
                       return_value = mock_parking_locations_return)
        self.get_driving_info_patch = \
            mock.patch(('mycity.intents.snow_parking_intent.g_maps_utils._get_driving_info'),
                       return_value = mock_get_driving_info_return)

        self.get_parking_location_patch.start()
        self.get_driving_info_patch.start()


    def tearDown(self):
        super().tearDown()
        self.csv_file.close()
        self.get_parking_location_patch.stop()
        self.get_driving_info_patch.stop()


