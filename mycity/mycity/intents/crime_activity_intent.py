"""Alexa intent used to find crime incidents"""

from dateutil.parser import parse
import mycity.intents.intent_constants as intent_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.utilities.crime_incidents_api_utils import \
    get_crime_incident_response
import logging

# Constants
CARD_TITLE_CRIME = "Crime Report"
RESPONSE_TEXT_TEMPLATE = \
    " {} an incident at {} with description {} categorized as {} occurred."
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

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in \
            mycity_request.session_attributes:
        address = mycity_request. \
            session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
        response = get_crime_incident_response(address)
        mycity_response.output_speech = \
            _build_text_from_response(response)
    else:
        logger.debug("Error: Called crime_incidents_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE_CRIME

    return mycity_response


def _build_text_from_response(response):
    """
    Parses the crime incident API response

    :param response: json data data object returned from crime incident API
    :return: a string containing formatted incident responses

    """
    print(response)
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
        incident[STREET_FIELD], incident[OFFENSE_FIELD],
        incident[OFFENSE_GROUP_FIELD])