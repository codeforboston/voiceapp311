import unittest
import unittest.mock as mock
import requests
import typing
from mycity.utilities.crime_incidents_api_utils import get_crime_incident_response


class ResponseStub:

    def __init__(self, status_code: int, response_data: typing.Dict = {}):
        self.status_code = status_code
        self.response_data = response_data

    def json(self):
        return self.response_data


class CrimeIncidentsAPIUtilitiesTestCase(unittest.TestCase):

    def test_get_crime_incident_response_returns_empty_dict_if_request_fails(self):
        requests_stub = _build_requests_stub(requests.codes.bad)
        to_test = get_crime_incident_response('46 Everdean St.', requests_stub)
        self.assertEquals({}, to_test)

    def test_get_crime_incident_response_returns_json_if_request_succeeds(self):
        expected = {'test': 'yes, it\'s a test'}
        requests_stub = _build_requests_stub(requests.codes.ok, expected)
        to_test = get_crime_incident_response('46 Everdean St.', requests_stub)
        self.assertEquals(expected, to_test)


def _build_requests_stub(status_code: int, data_from_service: typing.Dict = {}):
    requests_stub = requests
    requests_stub.Session.get = mock.MagicMock(return_value = ResponseStub(status_code, data_from_service))
    return requests_stub
