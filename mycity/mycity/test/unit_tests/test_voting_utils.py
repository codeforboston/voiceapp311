import mycity.test.unit_tests.base as base
import mycity.test.test_constants as test_constants
import mycity.utilities.voting_utils as vote_utils
import mycity.intents.intent_constants as intent_constants


class VotingUtilitiesTestCase(base.BaseTestCase):
    
    def test_get_ward_precinct_info(self):
        mock_resp = self._mock_response(status=200, 
            json_data=test_constants.MOCK_WARD_PRECINCT_RESP)
        mock_get.return_value = mock_resp
        expected_output_text = test_constants.WARD_PRECINCT
        result = vote_utils.get_ward_precinct_info(test_constants.COORDS, mock_resp)
        self.assertEquals(expected_output_text, result)

    def test_get_polling_location(self):
        mock_resp = self._mock_response(status=200, 
            json_data=test_constants.MOCK_POLL_RESP)
        mock_get.return_value = mock_resp
        expected_output_text = test_constants.POLL_DATA
        result = vote_utils.get_polling_location(test_constants.WARD_PRECINCT, mock_resp)
        self.assertEquals(expected_output_text, result)
