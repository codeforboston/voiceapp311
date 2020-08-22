"""
Functions for voting information including polling location information
"""

from . import intent_constants
import mycity.intents.speech_constants.voting_intent as speech_constants
from mycity.intents.user_address_intent \
    import request_user_address_response
from mycity.utilities.location_services_utils import \
    request_device_address_permission_response, \
    get_address_from_user_device, \
    is_address_in_city
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.mycity_request_data_model import MyCityRequestDataModel
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.voting_utils as vote_utils
import logging

logger = logging.getLogger(__name__)
CARD_TITLE = 'Voting Intent'
LOCATION_NAME = "Location Name"
LOCATION_ADDRESS = "Location Address"


def get_voting_location(mycity_request: MyCityRequestDataModel) -> \
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
    mycity_response.card_title = CARD_TITLE

    # check for address for locating voting location
    if intent_constants.CURRENT_ADDRESS_KEY not in \
        mycity_request.session_attributes:
        mycity_request, location_permissions = \
            get_address_from_user_device(mycity_request)
        if not location_permissions:
            return request_device_address_permission_response()
        elif intent_constants.CURRENT_ADDRESS_KEY not in \
                mycity_request.session_attributes:
            return request_user_address_response(mycity_request)
    
    current_address = \
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    top_candidate = gis_utils.geocode_address(current_address)

    ward_precinct = vote_utils.get_ward_precinct_info(top_candidate)
    poll_location = vote_utils.get_polling_location(ward_precinct)
    output_speech = speech_constants.LOCATION_SPEECH. \
        format(poll_location[LOCATION_NAME], poll_location[LOCATION_ADDRESS])
    
    mycity_response.output_speech = output_speech
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = True
    
    return mycity_response
