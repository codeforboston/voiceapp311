"""
Functions for voting information including polling location information
"""

from . import intent_constants
from mycity.intents.custom_errors import ParseError
from mycity.intents.user_address_intent \
    import request_user_address_response
from mycity.utilities.location_services_utils import \
    request_device_address_permission_response, \
    get_address_from_user_device, \
    is_address_in_city
from mycity.intents.user_address_intent import \
    clear_address_from_mycity_object
from mycity.utilities.address_utils import is_address_valid
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.mycity_request_data_model import MyCityRequestDataModel
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.voting_utils as vote_utils
import logging
import usaddress

logger = logging.getLogger(__name__)
CARD_TITLE = 'Voting Intent'
LOCATION_NAME = "Location Name"
LOCATION_ADDRESS = "Location Address"
LOCATION_SPEECH = "Your polling location is {}, {}"
NOT_IN_BOSTON_SPEECH = 'This address is not in Boston. ' \
                       'Please use this skill with a Boston address. '\
                       'See you later!'
ADDRESS_NOT_UNDERSTOOD = "I didn't understand that address, please try again with just the street number and name."
NO_WARD_OR_PRECINCT = "There doesn't seem to be information for that address in Boston"

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

    # If we have more specific info then just the street
    # address, make sure we are in Boston
    if not is_address_in_city(current_address):
        mycity_response.output_speech = NOT_IN_BOSTON_SPEECH
        mycity_response.should_end_session = True
        mycity_response.card_title = CARD_TITLE
        return mycity_response

    # grab relevant information from session address
    parsed_address, _ = usaddress.tag(current_address)

    if not is_address_valid(parsed_address):
        mycity_response.output_speech = ADDRESS_NOT_UNDERSTOOD
        mycity_response.dialog_directive = "ElicitSlotVotingIntent"
        mycity_response.reprompt_text = None
        mycity_response.session_attributes = mycity_request.session_attributes
        mycity_response.card_title = CARD_TITLE
        mycity_response.should_end_session = True
        return clear_address_from_mycity_object(mycity_response)


    top_candidate = gis_utils.geocode_address(current_address)
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = True

    try:
        ward_precinct = vote_utils.get_ward_precinct_info(top_candidate)
        poll_location = vote_utils.get_polling_location(ward_precinct)
        output_speech = LOCATION_SPEECH. \
            format(poll_location[LOCATION_NAME], poll_location[LOCATION_ADDRESS])
        mycity_response.output_speech = output_speech
    except ParseError:
        mycity_response.output_speech = NO_WARD_OR_PRECINCT
        
    return mycity_response
        
