"""Alexa intent used to find snow emergency parking"""

import mycity.intents.intent_constants as intent_constants
import mycity.intents.speech_constants.snow_parking_intent as constants
import mycity.intents.user_address_intent as user_address_intent
from mycity.intents.custom_errors import InvalidAddressError
from mycity.intents.speech_constants.location_speech_constants import \
    NOT_IN_BOSTON_SPEECH
from mycity.utilities.finder.FinderCSV import FinderCSV
import mycity.utilities.address_utils as address_utils
import mycity.utilities.location_services_utils as location_services_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel
import logging

PARKING_INFO_URL = "http://bostonopendata-boston.opendata.arcgis.com/" \
                   "datasets/53ebc23fcc654111b642f70e61c63852_0.csv"
SNOW_PARKING_CARD_TITLE = "Snow Parking"
ADDRESS_KEY = "Address"

logger = logging.getLogger(__name__)


def format_record_fields(record):
    """
    Updates the record fields by replacing the raw information with a sentence
    that provides context and will be more easily understood by users.

    :param record: a dictionary with driving time, driving_distance and all
        fields from the closest record
    :return: None
    """
    logger.debug('record: ' + str(record))
    record["Phone"] = constants.PHONE_PREPARED_STRING.format(record["Phone"]) \
        if record["Phone"].strip() != "" else constants.NO_PHONE
    record["Fee"] = constants.FEE_PREPARED_STRING.format(record["Fee"]) \
        if record["Fee"] != "No Charge" else constants.NO_FEE


def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response
    information.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('MyCityRequestDataModel received:' +
                 mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()

    coordinates = None
    if intent_constants.CURRENT_ADDRESS_KEY not in \
            mycity_request.session_attributes:
        # If not provided, try to get the user address through
        # geolocation and device address

        coordinates = address_utils.\
            get_address_coordinates_from_geolocation(mycity_request)

        if not coordinates:
            if mycity_request.device_has_geolocation:
                return location_services_utils.\
                    request_geolocation_permission_response()

            # Try getting registered device address
            mycity_request, location_permissions = location_services_utils.\
                get_address_from_user_device(mycity_request)
            if not location_permissions:
                return location_services_utils.\
                    request_device_address_permission_response()

    # If we don't have coordinates or an address by now, and we
    # have all required permissions, ask the user
    if not coordinates and intent_constants.CURRENT_ADDRESS_KEY not in \
            mycity_request.session_attributes:
        return user_address_intent.request_user_address_response(mycity_request)

    try:
        finder = FinderCSV(mycity_request, PARKING_INFO_URL, ADDRESS_KEY,
                           constants.OUTPUT_SPEECH_FORMAT, format_record_fields,
                           origin_coordinates=coordinates)
    except InvalidAddressError:
        mycity_response.output_speech = constants.ERROR_INVALID_ADDRESS
    else:
        if finder.is_in_city():
            logger.debug("Address or coords deemed to be in Boston:\n%s\n%s",
                         finder.origin_address, finder.origin_coordinates)
            finder_location_string = finder.origin_address \
                if finder.origin_address \
                else "{}, {}".format(finder.origin_coordinates['x'],
                                     finder.origin_coordinates['y'])
            print("Finding snow emergency parking for {}".
                  format(finder_location_string))
            finder.start()
            mycity_response.output_speech = finder.get_output_speech()
        else:
            logger.debug("Address or coords deemed to be NOT in Boston: "
                         "<address: %s> <coords: %s>", finder.origin_address,
                         finder.origin_coordinates)
            mycity_response.output_speech = NOT_IN_BOSTON_SPEECH

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = SNOW_PARKING_CARD_TITLE
    mycity_response.should_end_session = True

    return mycity_response
