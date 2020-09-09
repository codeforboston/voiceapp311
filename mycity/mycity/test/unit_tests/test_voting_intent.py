import mycity.test.unit_tests.base as base
import mycity.test.test_constants as test_constants
from mycity.intents.voting_intent import get_voting_location
import mycity.utilities.voting_utils as vote_utils
import mycity.intents.intent_constants as intent_constants
from mycity.mycity_request_data_model import MyCityRequestDataModel
from unittest.mock import patch
from mycity.intents.custom_errors import ParseError


import requests


class VotingIntentTestCase(base.BaseTestCase):

    @patch('mycity.intents.voting_intent.get_address_from_user_device')
    def test_get_voting_location_without_supplied_address(self, mock_get_address):
        mycity_request = MyCityRequestDataModel()
        mock_get_address.return_value = (MyCityRequestDataModel(), False)
        response = get_voting_location(mycity_request)
        self.assertTrue("read::alexa:device:all:address" in response.card_permissions)

    @patch('mycity.intents.voting_intent.gis_utils.geocode_address')
    @patch('mycity.intents.voting_intent.vote_utils.get_ward_precinct_info')
    @patch('mycity.intents.voting_intent.vote_utils.get_polling_location')
    def test_correct_voting_response(self, mock_poll_location, mock_ward, mock_geocode):
        mycity_request = MyCityRequestDataModel()
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "866 Huntington Avenue"
        mock_geocode.return_value = test_constants.GEOCODE_ADDRESS_CANDIDATES
        mock_ward.return_value = test_constants.WARD_PRECINCT
        mock_poll_location.return_value = test_constants.POLL_DATA
        expected_text = "Your polling location is BACK OF THE HILL APARTMENTS , 100 SOUTH HUNTINGTON AVENUE."
        response = get_voting_location(mycity_request)
        self.assertTrue(expected_text, response.output_speech)


    @patch('mycity.intents.voting_intent.gis_utils.geocode_address')
    @patch('mycity.intents.voting_intent.vote_utils.get_ward_precinct_info')
    def test_no_ward_voting_response(self, mock_ward, mock_geocode):
        mycity_request = MyCityRequestDataModel()
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "866 Huntington Avenue"
        mock_geocode.return_value = test_constants.GEOCODE_ADDRESS_CANDIDATES
        mock_ward.side_effect = ParseError()
        expected_text = "There doesn't seem to be information for that address in Boston"
        response = get_voting_location(mycity_request)
        self.assertTrue(expected_text, response.output_speech)
