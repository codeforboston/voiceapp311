"""
Functions for Alexa responses related to trash day
"""
from mycity.intents import intent_constants
from mycity.intents.custom_errors import \
    InvalidAddressError, BadAPIResponse, MultipleAddressError
from mycity.intents.user_address_intent import clear_address_from_mycity_object
import mycity.intents.speech_constants.trash_intent as speech_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.utilities.address_utils as address_utils
from streetaddress import StreetAddressParser

import collections
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
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]

        # grab relevant information from session address
        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)

        if not address_utils.is_address_valid(a):
            mycity_response.output_speech = speech_constants.ADDRESS_NOT_UNDERSTOOD
            mycity_response.dialog_directive = "ElicitSlotTrash"
            mycity_response.reprompt_text = None
            mycity_response.session_attributes = mycity_request.session_attributes
            mycity_response.card_title = CARD_TITLE
            mycity_response.should_end_session = True
            return clear_address_from_mycity_object(mycity_response)


        # currently assumes that trash day is the same for all units at
        # the same street address
        address = str(a['house']) + " " + str(a['street_full'])
        zip_code = str(a["other"]).zfill(5) if a["other"] and a["other"].isdigit() else None
        neighborhood = a["other"] if a["other"] and not a["other"].isdigit() else None

        zip_code_key = intent_constants.ZIP_CODE_KEY
        if zip_code is None and zip_code_key in \
                mycity_request.session_attributes:
            zip_code = mycity_request.session_attributes[zip_code_key]

        if "Neighborhood" in mycity_request.intent_variables and \
            "value" in mycity_request.intent_variables["Neighborhood"]:
            neighborhood = mycity_request.intent_variables["Neighborhood"]["value"]


        try:
            trash_days = get_trash_and_recycling_days(address, zip_code, neighborhood)
            trash_days_speech = build_speech_from_list_of_days(trash_days)

            mycity_response.output_speech = speech_constants.PICK_UP_DAY.format(trash_days_speech)
            mycity_response.should_end_session = True

        except InvalidAddressError:
            address_string = address
            if zip_code:
                address_string = address_string + " with zip code {}"\
                    .format(zip_code)
            if neighborhood:
                address_string = address_string + " in {}".format(neighborhood)
            mycity_response.output_speech = speech_constants.ADDRESS_NOT_FOUND.format(address_string)
            mycity_response.dialog_directive = "ElicitSlotTrash"
            mycity_response.reprompt_text = None
            mycity_response.session_attributes = mycity_request.session_attributes
            mycity_response.card_title = CARD_TITLE
            mycity_response.should_end_session = True
            return clear_address_from_mycity_object(mycity_response)

        except BadAPIResponse:
            mycity_response.output_speech = speech_constants.BAD_API_RESPONSE
            mycity_response.should_end_session = True
            
        except MultipleAddressError as error:
            addresses = [re.sub(r' \d{5}', '', address) for address in error.addresses]
            address_list = ', '.join(addresses)
            mycity_response.output_speech = speech_constants.MULTIPLE_ADDRESS_ERROR.format(address_list)
            mycity_response.dialog_directive = "ElicitSlotNeighborhood"
            mycity_response.should_end_session = False

    else:
        logger.error("Error: Called trash_day_intent with no address")
        mycity_response.output_speech = speech_constants.ADDRESS_NOT_UNDERSTOOD
        mycity_response.should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE
    return mycity_response


def get_trash_and_recycling_days(address, zip_code=None, neighborhood=None):
    """
    Determines the trash and recycling days for the provided address.
    These are on the same day, so only one array of days will be returned.

    :param address: String of address to find trash day for
    :param zip_code: Optional zip code to resolve multiple addresses
    :return: array containing next trash and recycling days
    :raises: InvalidAddressError, BadAPIResponse
    """
    logger.debug('address: ' + str(address) + ', zip_code: ' + str(zip_code) + ', neighborhood: {}' + str(neighborhood))
    api_params = get_address_api_info(address, zip_code, neighborhood)
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
    strings_to_compare = sorted(set(address["name"] for address in address_request_json), key=len, reverse=True)

    return [
        compare_a
        for i, compare_a in enumerate(strings_to_compare)
        if not any(compare_b in compare_a for compare_b in strings_to_compare[i + 1:])
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
    address_parser = StreetAddressParser()
    found_address = address_parser.parse(found_address)
    user_provided_address = address_parser.parse(user_provided_address)

    if found_address["house"] != user_provided_address["house"]:
        return False

    # Re-collect replaces South with S and North with N
    found_address["street_name"] = re.sub(r'^S\.? ', "South", found_address["street_name"])
    found_address["street_name"] = re.sub(r'^N\.? ', "North", found_address["street_name"])

    if found_address["street_name"].lower() != \
            user_provided_address["street_name"].lower():
        return False

    # Allow for mismatched "Road" street_type between user input and ReCollect API
    if "rd" in found_address["street_type"].lower() and \
        "road" in user_provided_address["street_type"].lower():
        return True

    # Allow fuzzy match on street type to allow "ave" to match "avenue"
    if found_address["street_type"].lower() not in \
        user_provided_address["street_type"].lower() and \
        user_provided_address["street_type"].lower() not in \
            found_address["street_type"].lower():
                return False


    return True


def get_address_api_info(address, provided_zip_code, neighborhood):
    """
    Gets the parameters required for the ReCollect API call

    :param address: Address to get parameters for
    :param provided_zip_code: Optional zip code used if we find multiple
        addresses
    :return: JSON object containing API parameters with format:

    {
        'area_name': value,
        'parcel_id': value,
        'service_id': value,
        'place_id': value,
        'area_id': value,
        'name': value
    }

    """
    logger.debug('address: ' + address +
                 'provided_zip_code: ' + str(provided_zip_code))
    base_url = "https://recollect.net/api/areas/" \
               "Boston/services/310/address-suggest"

    full_address = address if neighborhood is None else ' '.join([address, neighborhood])
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

    base_url = "https://recollect.net/api/places"
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
