import requests
import logging
from mycity.intents import intent_constants
from mycity.intents.speech_constants.location_speech_constants import \
    GENERIC_GEOLOCATION_PERMISSON_SPEECH, GENERIC_DEVICE_PERMISSON_SPEECH
import mycity.utilities.gis_utils as gis_utils
import mycity.mycity_response_data_model as mycity_response_data_model
import usaddress

""" Methods for working with location based data """
logger = logging.getLogger(__name__)


def get_address_from_user_device(mycity_request):
    """
    checks Amazon api for device address permissions. 
    If given, the address, if present, will be stored 
    in the session attributes
    :param mycity_request: MyCityRequestDataModel
    :param mycity_response: MyCityResponseDataModel
    :return : MyCityRequestModel object and boolean indicating if we have
        device address permissions
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.
                 get_logger_string())

    base_url = "https://api.amazonalexa.com/v1/devices/{}" \
        "/settings/address".format(mycity_request.device_id)
    head_info = {'Accept': 'application/json',
                 'Authorization': 'Bearer {}'.format(mycity_request.
                                                     api_access_token)}
    response_object = requests.get(base_url, headers=head_info)

    logger.debug("response object:{}".format(response_object))
    res = response_object.json()
    if response_object.status_code == 200 and res['addressLine1'] is not None:
        address = res['addressLine1']
        state = res['stateOrRegion']
        city = res['city']
        current_address = " ".join([address, city, state])
        mycity_request.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY] = current_address
    return mycity_request, response_object.status_code == 200


def request_geolocation_permission_response():
    """
    Builds a response object for requesting geolocation permissions. The
    returned object's speech can be modified if you want to add more information.

    :return MyCityResponseDataModel: MyCityResponseDataModel with required fields
        to request geolocation access
    """
    response = mycity_response_data_model.MyCityResponseDataModel()
    response.output_speech = GENERIC_GEOLOCATION_PERMISSON_SPEECH
    response.card_type = "AskForPermissionsConsent"
    response.card_permissions = ["alexa::devices:all:geolocation:read"]
    response.should_end_session = True
    return response


def request_device_address_permission_response():
    """
    Builds a response object for requesting geolocation permissions. The
    returned object's speech can be modified if you want to add more information.

    :return MyCityResponseDataModel: MyCityResponseDataModel with required fields
        to request geolocation access
    """
    response = mycity_response_data_model.MyCityResponseDataModel()
    response.output_speech = GENERIC_DEVICE_PERMISSON_SPEECH
    response.card_type = "AskForPermissionsConsent"
    response.card_permissions = ["read::alexa:device:all:address"]
    response.should_end_session = True
    return response


def convert_mycity_coordinates_to_arcgis(mycity_request) -> dict:
    """
    Gets coordinates from a MyCityRequestDataModel and converts them to dictionary
    required by GIS utilities

    :param mycity_request: MyCityRequstDataModel containing geolocation coordinates
        to convert
    :return dictionary: x, y coordinates of device location
    """
    gis_coordinates = {
        'x': 0,
        'y': 0
    }
    
    if mycity_request.geolocation_coordinates:
        gis_coordinates['y'] = mycity_request.geolocation_coordinates["latitudeInDegrees"]
        gis_coordinates['x'] = mycity_request.geolocation_coordinates["longitudeInDegrees"]

    return gis_coordinates


def is_in_city(mycity_request, city):
    """
    Reverse geo-locate the session's coordinates to determine if the device is
    in Boston
    :param city: City to check reverse geo-location to
    :param mycity_request: MyCityRequestDataModel
    :return: True or False
    """
    logger.debug('MyCityRequestDataModel received:' +
                 mycity_request.get_logger_string())

    if mycity_request.geolocation_coordinates:
        return are_coordinates_in_city(
            mycity_request.geolocation_coordinates,
            [city])

    return True


def are_coordinates_in_city(coordinates, cities):
    """
    Checks if the provided coordinates are in any
    of the cities provided
    :param coordinates: Dictionary of coordinates
    :param cities: Array of possible cities to check against
    :return: True if coordinates are in one of the cities. False if not.
    """
    if 'latitudeInDegrees' in coordinates:
        coordinates['y'] = coordinates["latitudeInDegrees"]
        coordinates['x'] = coordinates["longitudeInDegrees"]

    lat = coordinates['y']
    long = coordinates['x']

    location = gis_utils.reverse_geocode_addr([long, lat])
    if location['address']['City'] in cities or \
            location['address']['Region'] != 'Massachusetts':
        return False

    return True


def is_address_in_city(address):
    """
    Check if the provided address is in Boston
    :param address: the adress to check
    :return: boolean
    """

    # If we don't have any detail about city or zipcode
    # we default to Boston for the geocode search
    parsed_address, _ = usaddress.tag(address)
    if "PlaceName" not in parsed_address and "ZipCode" not in parsed_address:
        address = " ".join([address, "Boston"])

    city = 'Boston Metro Area'
    return gis_utils.geocode_addr(address, city)


def is_location_in_city(address, coordinates):
    """
    Determines if the provided address or coordinates
    are located in Boston. If both are provided,
    address takes priority
    :param address: String of address to check. Can be None.
    :param coordinates: Dictionary of coordinates to check. Can be None.
    :return: True if location is in Boston. False if not.
    """
    if address:
        return is_address_in_city(address)
    if coordinates:
        return are_coordinates_in_city(coordinates, gis_utils.NEIGHBORHOODS)

    return True
