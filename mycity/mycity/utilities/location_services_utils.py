import requests
import logging
from mycity.intents import intent_constants
import mycity.utilities.gis_utils as gis_utils
import mycity.mycity_response_data_model as mycity_response_data_model
from streetaddress import StreetAddressParser

""" Methods for working with location based data """
logger = logging.getLogger(__name__)

GENERIC_GEOLOCATION_PERMISSON_SPEECH = """
    Boston Info would like to use your location. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions."""

GENERIC_DEVICE_PERMISSON_SPEECH = """
    Boston Info would like to use your device's address. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions."""


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
        current_address = res['addressLine1']
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
        lat = mycity_request.geolocation_coordinates['latitudeInDegrees']
        long = mycity_request.geolocation_coordinates['longitudeInDegrees']
        location = gis_utils.reverse_geocode_addr([long, lat])
        if location['address']['City'] != city or \
                location['address']['Region'] != 'Massachusetts':
            return False

    return True


def is_current_address_in_city(mycity_request, city):
    """
    Checks that the address set for the current session is
    located in provided city. If the city can't be determined,
    returns True.
    :param mycity_request: MyCityRequestDataModel
    :param city: City to check is in address
    """
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)

        other_address = a["other"]
        if other_address and not other_address.isdigit() and city not in other_address:
            return False

    return True
