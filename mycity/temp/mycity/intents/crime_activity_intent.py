"""Alexa intent used to find crime incidents"""

import logging
import mycity.intents.intent_constants as intent_constants
from mycity.intents.user_address_intent \
    import request_user_address_response
from mycity.utilities.location_services_utils import is_location_in_city
from mycity.intents.speech_constants.location_speech_constants import \
    NOT_IN_BOSTON_SPEECH
from dateutil.parser import parse
from mycity.utilities.location_services_utils \
    import request_geolocation_permission_response, \
    request_device_address_permission_response, \
    get_address_from_user_device
from mycity.utilities.address_utils \
    import get_address_coordinates_from_geolocation
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.utilities.crime_incidents_api_utils import \
    get_crime_incident_response
import mycity.utilities.gis_utils as gis_utils

# Constants
CARD_TITLE_CRIME = "Crime Report"
RESPONSE_TEXT_TEMPLATE = " {} an incident at {} occurred categorized as {}."
ERROR_RESPONSE = "An error occurred requesting crime incidents for this address"
NO_RESULT_RESPONSE = "We found no incidents in that area"

# Crime API response fields
OFFENSE_FIELD = "OFFENSE_DESCRIPTION"
OFFENSE_GROUP_FIELD = "OFFENSE_CODE_GROUP"
STREET_FIELD = "STREET"
DATE_FIELD = "OCCURRED_ON_DATE"
SUCCESS_FIELD = "success"
RESULT_FIELD = "result"
RECORDS_FIELD = "records"

logger = logging.getLogger(__name__)


def get_crime_incidents_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with crime incidents response information.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('[method: get_crime_incidents_intent]')

    coordinates = {}
    current_address = None
    if intent_constants.CURRENT_ADDRESS_KEY not in \
            mycity_request.session_attributes:
        coordinates = get_address_coordinates_from_geolocation(mycity_request)

        if not coordinates:
            if mycity_request.device_has_geolocation:
                return request_geolocation_permission_response()

            # Try getting registered device address
            mycity_request, location_permissions \
                = get_address_from_user_device(mycity_request)
            if not location_permissions:
                return request_device_address_permission_response()

    # Convert address to coordinates if we only have user address
    if intent_constants.CURRENT_ADDRESS_KEY \
            in mycity_request.session_attributes:
        current_address = mycity_request.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY]
        coordinates = gis_utils.geocode_address(current_address)

    # If we don't have coordinates by now, and we have all required
    #  permissions, ask the user for an address
    if not coordinates:
        return request_user_address_response(mycity_request)

    mycity_response = MyCityResponseDataModel()

    # If our address/coordinates are not in Boston, send a response letting
    # the user know the intent only works in Boston.
    if not is_location_in_city(current_address, coordinates):
        mycity_response.output_speech = NOT_IN_BOSTON_SPEECH
    else:
        response = get_crime_incident_response(coordinates)
        mycity_response.output_speech = \
            _build_text_from_response(response)

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE_CRIME
    mycity_response.should_end_session = True

    return mycity_response


def _build_text_from_response(response):
    """
    Parses the crime incident API response

    :param response: json data data object returned from crime incident API
    :return: a string containing formatted incident responses

    """
    text_response = ""
    if bool(response[SUCCESS_FIELD]):
        for incident in response[RESULT_FIELD][RECORDS_FIELD]:
            text_response += _build_text_from_record(incident)
        if text_response.strip() == "":
            text_response = NO_RESULT_RESPONSE
    else:
        logger.debug("An error occurred during incident request: {}"
                     .format(response))
        text_response = ERROR_RESPONSE
    return text_response


def _build_text_from_record(incident):
    """
    Builds the text response for a single crime incident record

    :param incident: a crime incident object
    :return: a string containing the formatted response for a single incident

    """
    dt = parse(incident[DATE_FIELD])
    return RESPONSE_TEXT_TEMPLATE.format(
        dt.strftime("On %A %d of %B %Y at %I:%M%p"),
        incident[STREET_FIELD], incident[OFFENSE_GROUP_FIELD])
