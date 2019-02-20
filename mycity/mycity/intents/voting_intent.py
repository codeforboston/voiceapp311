"""
Functions for voting information including polling location information
"""

from . import intent_constants
import mycity.intents.speech_constants.voting_intent as speech_constants
from streetaddress import StreetAddressParser
from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.utilities.arcgis_utils as arcgis_utils
import requests
import logging

logger = logging.getLogger(__name__)
CARD_TITLE = "Voting Intent"


def get_polling_location(mycity_request):
    """
    Generates response object for a polling location inquiry which includes
    a user's location to vote.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """

    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())
    mycity_response = MyCityResponseDataModel()
    
    current_address = \
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    current_address += ", Boston, MA"
    candidates = arcgis_utils.geocode_address_candidates(current_address)
    top_candidate = arcgis_utils.select_top_address_candidate(candidates)
    ward_precinct = arcgis_utils.get_ward_precinct_info(top_candidates)
    poll_location = arcgis_utils.get_polling_location(ward_precinct)
    output_speech = speech_constants.LOCATION_SPEECH.format(poll_location["Location Name"], poll_location["Location Address"])
    mycity_response.output_speech = output_speech
    mycity_response.reprompt_text = None
    mycity_response.reprompt_text = CARD_TITLE
    mycity_response.should_end_session = True
    return mycity_response
