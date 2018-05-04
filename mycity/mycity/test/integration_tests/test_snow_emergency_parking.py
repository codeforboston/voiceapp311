import unittest.mock as mock

import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.test_constants as test_constants


##########################################
# TestCase class for snow_parking_intent #
##########################################

class SnowEmergencyTestCase(mix_ins.IntentRepromptTextTestMixIn, 
                            mix_ins.IntentCardTitleTestMixIn,
                            mix_ins.IntentTestForErrorMixIn,
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
        self.closest_parking_location_patch = \
            mock.patch(('mycity.intents.snow_parking_intent.'
                        '_get_closest_parking_location'),
                       return_value = test_constants.CLOSEST_PARKING_MOCK_RETURN)
        self.get_closest_feature_patch = \
            mock.patch(('mycity.intents.location_utils.get_closest_feature'),
                       return_value = test_constants.GET_PARKING_DATA_MOCK_RETURN)

        self.closest_parking_location_patch.start()
        self.get_closest_feature_patch.start()


    def tearDown(self):
        super().tearDown()
        self.closest_parking_location_patch.stop()
        self.get_closest_feature_patch.stop()


