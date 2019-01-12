import unittest.mock as mock
import mycity.test.test_constants as test_constants
import mycity.test.unit_tests.base as base
from mycity.utilities.crime_incidents_api_utils import \
    get_crime_incident_response

class CrimeIncidentsAPIUtilitiesTestCase(base.BaseTestCase):

    @mock.patch(
        'mycity.utilities.gis_utils.geocode_address',
        return_value=test_constants.GEOCODE_ADDRESS_MOCK
    )
    @mock.patch('requests.get')
    def test_get_crime_incident_response(self, mock_geocode_address, mock_get):
        mock_resp = self._mock_response(status=200,
            json_data=test_constants.GET_CRIME_INCIDENTS_API_MOCK)
        mock_get.return_value = mock_resp

        test_address = "46 Everdean St Boston, MA"
        result = get_crime_incident_response(test_address)
        self.assertEqual(
            True,
            result['success']
        )
