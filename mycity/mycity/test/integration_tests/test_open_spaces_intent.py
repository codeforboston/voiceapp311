import csv
import unittest.mock as mock

import mycity.utilities.google_maps_utils as g_maps_utils
import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.test.test_constants as test_constants


#############################################
# TestCase class for get_open_spaces_intent #
#############################################

class OpenSpacesTestCase(mix_ins.RepromptTextTestMixIn,
                         mix_ins.CardTitleTestMixIn,
                         mix_ins.CorrectSpeechOutputTestMixIn,
                         base_case.IntentBaseCase):

    intent_to_test = "OpenSpacesIntent"
    returns_reprompt_text = False

    def setUp(self):
        """
        Functions to patch:
            get_open_spaces
            _get_driving_info
        """
        super().setUp()
        self.csv_file = open(test_constants.OPEN_SPACES_TEST_CSV, 
                             encoding = 'utf-8-sig')
        mock_get_open_spaces_return = csv.reader(self.csv_file, delimiter = ',')
        mock_get_driving_info_return = \
            test_constants.CLOSEST_OPEN_SPACES_DRIVING_DATA
        self.get_open_spaces_patch = \
            mock.patch(('mycity.intents.get_open_spaces_intent.'
                        '_get_open_spaces'),
                       return_value = mock_get_open_spaces_return)
        self.get_driving_info_patch = \
            mock.patch(('mycity.intents.get_open_spaces_intent.g_maps_utils.'
                        '_get_driving_info'),
                       return_value = mock_get_driving_info_return)
        self.get_open_spaces_patch.start()
        self.get_driving_info_patch.start()


    def tearDown(self):
        super().tearDown()
        self.csv_file.close()
        self.get_open_spaces_patch.stop()
        self.get_driving_info_patch.stop()


