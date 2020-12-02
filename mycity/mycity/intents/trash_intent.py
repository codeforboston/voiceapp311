"""
Functions for Alexa responses related to trash day
"""
from mycity.intents.speech_constants.location_speech_constants import \
    NOT_IN_BOSTON_SPEECH
from mycity.utilities.location_services_utils import \
    request_device_address_permission_response, \
    get_address_from_user_device, \
    is_address_in_city
from mycity.intents import intent_constants
from mycity.intents.custom_errors import \
    InvalidAddressError, BadAPIResponse, MultipleAddressError
from mycity.intents.user_address_intent import \
    clear_address_from_mycity_object, request_user_address_response
import mycity.intents.speech_constants.trash_intent as speech_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.utilities.address_utils as address_utils
import usaddress


import re
import requests
import logging

logger = logging.getLogger(__name__)

DAY_CODE_REGEX = r'\d+A? - '
CARD_TITLE = "Trash Day"


def get_trash_day_info(mycity_request):
    """
    Generates response object for a trash day inquiry.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('MyCityRequestDataModel received:' +
                 mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()

    # Determine if we have required address information. Request if we do not.
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

    # grab relevant information from session address
    parsed_address, _ = usaddress.tag(current_address)

    if not address_utils.is_address_valid(parsed_address):
        repeatCount = mycity_request.session_attributes[intent_constants.REPEAT_COUNT]
        mycity_response.output_speech = speech_constants.ADDRESS_NOT_UNDERSTOOD \
            if repeatCount <= 0 else speech_constants.ADDRESS_NOT_FOUND.format(current_address)
        if repeatCount <= 0:
            mycity_response.dialog_directive = "ElicitSlotTrash" 
        mycity_response.reprompt_text = None
        mycity_response.session_attributes = mycity_request.session_attributes
        mycity_response.card_title = CARD_TITLE
        mycity_response.should_end_session = False if repeatCount <= 0 else True
        repeatCount += 1
        mycity_response.session_attributes[intent_constants.REPEAT_COUNT] = repeatCount
        return clear_address_from_mycity_object(mycity_response)

    # If we have more specific info then just the street
    # address, make sure we are in Boston
    if not is_address_in_city(current_address):
        mycity_response.output_speech = NOT_IN_BOSTON_SPEECH
        mycity_response.should_end_session = True
        mycity_response.card_title = CARD_TITLE
        return mycity_response

    # currently assumes that trash day is the same for all units at
    # the same street address
    address = " ".join([
        parsed_address['AddressNumber'],
        parsed_address['StreetName'],
        parsed_address['StreetNamePostType']])
    neighborhood = parsed_address["PlaceName"] \
        if "PlaceName" in parsed_address \
        and not parsed_address["PlaceName"].isdigit() \
        else None

    if "Neighborhood" in mycity_request.intent_variables and \
        "value" in mycity_request.intent_variables["Neighborhood"]:
            neighborhood = \
                mycity_request.intent_variables["Neighborhood"]["value"]

    try:
        trash_days = get_trash_and_recycling_days(address, neighborhood)
        trash_days_speech = build_speech_from_list_of_days(trash_days)

        mycity_response.output_speech = speech_constants.PICK_UP_DAY.\
            format(trash_days_speech)
        mycity_response.should_end_session = True

    except InvalidAddressError:
        address_string = address
        mycity_response.output_speech = speech_constants.ADDRESS_NOT_FOUND.\
            format(address_string)
        mycity_response.dialog_directive = "ElicitSlotTrash"
        mycity_response.reprompt_text = None
        mycity_response.session_attributes = mycity_request.session_attributes
        mycity_response.card_title = CARD_TITLE
        mycity_response.should_end_session = False
        return clear_address_from_mycity_object(mycity_response)

    except BadAPIResponse:
        mycity_response.output_speech = speech_constants.BAD_API_RESPONSE
        mycity_response.should_end_session = True

    except MultipleAddressError as error:
        addresses = [re.sub(r' \d{5}', '', address) for address in
                     error.addresses]
        address_list = ', '.join(addresses)
        mycity_response.output_speech = speech_constants.\
            MULTIPLE_ADDRESS_ERROR.format(address_list)
        mycity_response.dialog_directive = "ElicitSlotNeighborhood"
        mycity_response.should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE
    return mycity_response


def get_trash_and_recycling_days(address, neighborhood=None):
    """
    Determines the trash and recycling days for the provided address.
    These are on the same day, so only one array of days will be returned.

    :param neighborhood:
    :param address: String of address to find trash day for
    :return: array containing next trash and recycling days
    :raises: InvalidAddressError, BadAPIResponse
    """
    logger.debug('address: ' + str(address) +
                 ', neighborhood: {}' + str(neighborhood))
    api_params = get_address_api_info(address, neighborhood)
    if not api_params:
        raise InvalidAddressError

    if not validate_found_address(api_params["name"], address):
        logger.debug("InvalidAddressError")
        raise InvalidAddressError

    trash_data = get_trash_day_data(api_params)
    if not trash_data:
        raise BadAPIResponse

    trash_and_recycling_days = get_trash_days_from_trash_data(trash_data)

    return trash_and_recycling_days


def find_unique_addresses(address_request_json):
    """
    Finds unique addresses in a provided address request json returned
    from the ReCollect service
    :param address_request_json: json object returned from ReCollect address
        request service
    :return: list of unique addresses
    """
    logger.debug('address_request_json: ' + str(address_request_json))
    # Pre-extract the addresses from the payload and uniquify them
    strings_to_compare = sorted(set(address["name"] for address in
                                    address_request_json),
                                key=len, reverse=True)

    return [
        compare_a
        for i, compare_a in enumerate(strings_to_compare)
        if not any(compare_b in compare_a for compare_b in
                   strings_to_compare[i + 1:])
    ]


def validate_found_address(found_address, user_provided_address):
    """
    Validates that the street name and number found in trash collection
    database matches the provided values. We do not treat partial matches
    as valid.

    :param found_address: Full address found in trash collection database
    :param user_provided_address: Street number and name provided by user
    :return: boolean: True if addresses are considered a match, else False
    """
    logger.debug('found_address: ' + str(found_address) +
                 'user_provided_address: ' + str(user_provided_address))
    found_address, _ = usaddress.tag(found_address)
    user_provided_address, _ = usaddress.tag(user_provided_address)

    if found_address["AddressNumber"] != user_provided_address["AddressNumber"]:
        return False

    # Re-collect replaces South with S and North with N
    found_address["StreetName"] = re.sub(r'^S\.? ', "South ",
                                         found_address["StreetName"])
    found_address["StreetName"] = re.sub(r'^N\.? ', "North ",
                                         found_address["StreetName"])

    if found_address["StreetName"].lower() != \
            user_provided_address["StreetName"].lower():
        return False

    # Allow for mismatched Road street_type between user input and ReCollect API
    if "rd" in found_address["StreetNamePostType"].lower() and \
        "road" in user_provided_address["StreetNamePostType"].lower():
        return True

    # Allow fuzzy match on street type to allow "ave" to match "avenue"
    if "StreetNamePostType" in found_address and \
        "StreetNamePostType" in user_provided_address:

        if found_address["StreetNamePostType"].lower() not in \
            user_provided_address["StreetNamePostType"].lower() and \
            user_provided_address["StreetNamePostType"].lower() not in \
                found_address["StreetNamePostType"].lower():
                    return False


    return True


def get_address_api_info(address, neighborhood):
    """
    Gets the parameters required for the ReCollect API call

    :param address: Address to get parameters for
    :return: JSON object containing API parameters with format:

    {
        'area_name': value,
        'parcel_id': value,
        'service_id': value,
        'place_id': value,
        'area_id': value,
        'name': value,
        'start_date': value,
        'end_date': value
    }

    """
    logger.debug('address: ' + address)
    base_url = "https://recollect.net/api/areas/" \
               "Boston/services/310/address-suggest"

    full_address = address if neighborhood is None else ' '.join([address,
                                                                  neighborhood])
    url_params = {'q': full_address, 'locale': 'en-US'}
    request_result = requests.get(base_url, url_params)

    if request_result.status_code != requests.codes.ok:
        logger.debug('Error getting ReCollect API info. Got response: {}'
                     .format(request_result.status_code))
        return {}

    result_json = request_result.json()
    if not result_json:
        return {}

    unique_addresses = find_unique_addresses(result_json)
    if len(unique_addresses) > 1:
        raise MultipleAddressError(unique_addresses)

    api_params = result_json[0]
    api_params['start_date'] = 
    return result_json[0]


def get_trash_day_data(api_parameters):
    """
    Gets the trash day data from ReCollect using the provided API parameters

    :param api_parameters: Parameters for ReCollect API
    :return: JSON object containing all trash data
    """
    logger.debug('api_parameters: ' + str(api_parameters))
    # Rename the default API parameter "name" to "formatted_address"
    if "name" in api_parameters:
        api_parameters["formatted_address"] = api_parameters.pop("name")

    base_url = "https://api.recollect.net/api/places/{}/services/{}/events"
    request_result = requests.get(base_url, api_parameters)

    if request_result.status_code != requests.codes.ok:
        logger.debug("Error getting trash info from ReCollect API info. " \
                     "Got response: {}".format(request_result.status_code))
        return {}

    return request_result.json()


def get_trash_days_from_trash_data(trash_data):
    """
    Parse trash data from ReCollect service and return the trash and recycling
    days.

    :param trash_data: Trash data provided from ReCollect API
    :return: An array containing days trash and recycling are picked up
    :raises: BadAPIResponse
    """
    logger.debug('trash_data: ' + str(trash_data))
    try:
        trash_days_string = trash_data["next_event"]["zone"]["title"]
        trash_days_string = re.sub(DAY_CODE_REGEX, '', trash_days_string)
        trash_days = trash_days_string.replace('&', '').split()
    except KeyError:
        # ReCollect API returned an unexpected JSON format
        raise BadAPIResponse

    return trash_days


def build_speech_from_list_of_days(days):
    """
    Converts a list of days into proper speech, such as adding the word 'and'
    before the last item.

    :param days: String array of days
    :return: Speech representing the provided days
    :raises: BadAPIResponse
    """
    logger.debug('days: ' + str(days))
    if len(days) == 0:
        raise BadAPIResponse

    if len(days) == 1:
        return days[0]
    elif len(days) == 2:
        output_speech = " and ".join(days)
    else:
        output_speech = ", ".join(days[0:-1])
        output_speech += ", and {}".format(days[-1])

    return output_speech
