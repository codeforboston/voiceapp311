import mycity.test.unit_tests.base as base
import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.utilities.arcgis_utils as arcgis_utils
import mycity.mycity_controller as my_con
import mycity.intents.intent_constants as intent_constants


class ArcgisUtilitiesTestCase(base.BaseTestCase):
    
    @mock.patch('requests.request')
    def test_get_ward_precinct_info(self, mock_get):
        mock_resp = self._mock_response(status=200, 
            json_data=test_constants.MOCK_WARD_PRECINCT_RESP)
        mock_get.return_value = mock_resp
        expected_output_text = test_constants.WARD_PRECINCT
        result = arcgis_utils.get_ward_precinct_info(test_constants.COORDS)
        self.assertEquals(expected_output_text, result)