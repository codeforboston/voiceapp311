import unittest.mock as mock

import mycity.test.test_constants as test_constants
import mycity.test.unit_tests.base as base
import mycity.utilities.google_maps_utils as g_maps_utils


class TestGoogleMapsUtilities(base.BaseTestCase):

    def test_parse_closest_location_info(self):
        location_type = 'Fake location'
        closest_location_info = {'Driving distance': 'fake',
                              'Driving distance text': 'also fake',
                              'Driving time': 'triply fake',
                              'Driving time text': 'fake like a mug',
                              location_type: 'fake fake fake fake'}
        to_test = g_maps_utils._parse_closest_location_info(location_type, closest_location_info)
        self.assertIn(g_maps_utils.DRIVING_DISTANCE_TEXT_KEY, to_test)
        self.assertIn(g_maps_utils.DRIVING_TIME_TEXT_KEY, to_test)
        self.assertIn(location_type, to_test)
        self.assertNotIn('Driving time', to_test)
        self.assertNotIn('Driving distance', to_test)

    def test_setup_google_maps_query_params(self):
        origin = "46 Everdean St Boston, MA"
        dests = ["123 Fake St Boston, MA", "1600 Penn Ave Washington, DC"]
        to_test = g_maps_utils._setup_google_maps_query_params(origin, dests)
        self.assertEqual(origin, to_test["origins"])
        self.assertEqual(dests, to_test["destinations"].split("|"))
        self.assertEqual("imperial", to_test["units"])    
