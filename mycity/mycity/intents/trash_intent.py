"""
Functions for Alexa responses related to trash day
"""
from .custom_errors import InvalidAddressError, BadAPIResponse
from streetaddress import StreetAddressParser
from mycity.mycity_response_data_model import MyCityResponseDataModel
import re
import requests
from . import intent_constants


def get_trash_day_info(mycity_request):
    """
    Generates response object for a trash day inquiry.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    
    print(
        '[module: trash_intent]',
        '[method: get_trash_day_info]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]

        # grab relevant information from session address
        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        # currently assumes that trash day is the same for all units at
        # the same street address
        address = str(a['house']) + " " + str(a['street_name'])
        zip_code = str(a["other"]) if a["other"] else None

        try:
            trash_days = get_trash_and_recycling_days(address, zip_code)
            trash_days_speech = build_speech_from_list_of_days(trash_days)

            mycity_response.output_speech = "Trash and recycling is picked up on {}."\
                .format(trash_days_speech)

        except InvalidAddressError:
            address_string = address
            if zip_code:
                address_string = address_string + " with zip code {}"\
                    .format(zip_code)
            mycity_response.output_speech =\
                "I can't seem to find {}. Try another address"\
                .format(address_string)
        except BadAPIResponse:
            mycity_response.output_speech =\
                "Hmm something went wrong. Maybe try again?"
        except MultipleAddressError:
            mycity_response.output_speech \
                = "I found multiple places with the address {}. Try "\
                "specifying the zip code.".format(address)

        mycity_response.should_end_session = False
    else:
        print("Error: Called trash_day_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name
    return mycity_response


def get_trash_and_recycling_days(address, zip_code=None):
    """
    Determines the trash and recycling days for the provided address.
    These are on the same day, so only one array of days will be returned.

    :param address: String of address to find trash day for
    :param zip_code: Optional zip code to resolve multiple addresses
    :return: array containing next trash and recycling days
    """

    api_params = get_address_api_info(address, zip_code)
    if not api_params:
        raise InvalidAddressError

    trash_data = get_trash_day_data(api_params)
    if not trash_data:
        raise BadAPIResponse

    trash_and_recycling_days = get_trash_days_from_trash_data(trash_data)

    return trash_and_recycling_days


def find_unique_zipcodes(address_request_json):
    """
    Finds unique zip codes in a provided address request json returned
    from the ReCollect service
    :param address_request_json: json object returned from ReCollect address
        request service
    :return: dictionary with zip code keys and value list of indexes with that
        zip code
    """

    found_zip_codes = {}
    for index, address_info in enumerate(address_request_json):
        zip_code = re.search('\d{5}', address_info["name"]).group(0)
        if zip_code:
            if zip_code in found_zip_codes:
                found_zip_codes[zip_code].append(index)
            else:
                found_zip_codes[zip_code] = [index]

    return found_zip_codes


def get_address_api_info(address, provided_zip_code=None):
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

    base_url = "https://recollect.net/api/areas/" \
               "Boston/services/310/address-suggest"
    url_params = {'q': address, 'locale': 'en-US'}
    request_result = requests.get(base_url, url_params)

    if request_result.status_code != requests.codes.ok:
        print("Error getting ReCollect API info. Got response: {}"
              .format(request_result.status_code))
        return {}

    result_json = request_result.json()
    if not result_json:
        return {}

    unique_zip_codes = find_unique_zipcodes(result_json)
    if len(unique_zip_codes) > 1:
        # If we have a provided zip code, see if it is in the request results
        if provided_zip_code:
            if provided_zip_code in unique_zip_codes:
                return result_json[unique_zip_codes[provided_zip_code][0]]

            else:
                return {}

        raise MultipleAddressError

    return result_json[0]


def get_trash_day_data(api_parameters):
    """
    Gets the trash day data from ReCollect using the provided API parameters

    :param api_parameters: Parameters for ReCollect API
    :return: JSON object containing all trash data
    """

    # Rename the default API parameter "name" to "formatted_address"
    if "name" in api_parameters:
        api_parameters["formatted_address"] = api_parameters.pop("name")

    base_url = "https://recollect.net/api/places"
    request_result = requests.get(base_url, api_parameters)

    if request_result.status_code != requests.codes.ok:
        print("Error getting trash info from ReCollect API info. "
              "Got response: {}".format(request_result.status_code))
        return {}

    return request_result.json()


def get_trash_days_from_trash_data(trash_data):
    """
    Parse trash data from ReCollect service and return the trash and recycling
    days.

    :param trash_data: Trash data provided from ReCollect API
    :return: An array containing days trash and recycling are picked up
    """

    try:
        trash_days_string = trash_data["next_event"]["zone"]["title"]
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
    """
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
