"""
Functions for voting information including polling location information
"""

from . import intent_constants
import mycity.intents.speech_constants.voting_intent as speech_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.mycity_request_data_model import MyCityRequestDataModel
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.voting_utils as vote_utils
import logging

logger = logging.getLogger(__name__)
CARD_TITLE = 'Voting Intent'


def get_polling_location(mycity_request: MyCityRequestDataModel) -> \
        MyCityResponseDataModel:
    """
    Generates response object for a polling location inquiry which includes
    a user's location to vote.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """

    logger.debug('MyCityRequestDataModel received:' +
                 mycity_request.get_logger_string())
    mycity_response = MyCityResponseDataModel()
    
    current_address = \
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    top_candidate = gis_utils.geocode_address(current_address)

    # If an address has a score below 90, most likely it does not exist or fake
    if not top_candidate:
        mycity_response.output_speech = 'I could not find a matching ' \
                                        'address, please try again with ' \
                                        'a different one.'
    else:
        ward_precinct = vote_utils.get_ward_precinct_info(top_candidate)
        poll_location = vote_utils.get_polling_location(ward_precinct)
        output_speech = speech_constants.LOCATION_SPEECH.\
            format(poll_location["Location Name"],
                   poll_location["Location Address"])
        mycity_response.output_speech = output_speech
        mycity_response.reprompt_text = None
        mycity_response.reprompt_text = CARD_TITLE
        mycity_response.should_end_session = True
    return mycity_response
