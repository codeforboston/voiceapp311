import unittest
from mycity.utilities.crime_incidents_api_utils import get_crime_incident_response


class CrimeIncidentsAPIUtilitiesTestCase(unittest.TestCase):

    def test_get_crime_incident_response_returns_success_if_query_is_successful(self):
        test_address = "46 Everdean St Boston, MA"
        result = get_crime_incident_response(test_address)
        self.assertEqual(True, result['success'])
