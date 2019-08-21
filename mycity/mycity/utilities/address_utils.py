"""
Utility function for building an address string from a mycity request

"""

import mycity.utilities.gis_utils as gis_utils
import mycity.intents.intent_constants as intent_constants
import mycity.utilities.location_services_utils as location_services_utils
import logging

from streetaddress import StreetAddressParser
from mycity.intents.custom_errors import InvalidAddressError

logger = logging.getLogger(__name__)


def build_origin_address(req):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified

    :param req: MyCityRequestDataModel object
    :return: String containing full address
    """
    logger.debug('MyCityRequestDataModel received:' + req.get_logger_string())
    address_parser = StreetAddressParser()
    current_address = \
        req.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    parsed_address = address_parser.parse(current_address)
    if parsed_address["house"] is None or parsed_address["street_full"] is None:
        logger.debug("Parsed address had an unexpected None part in {house: %r, street_full: %r}",
                     parsed_address["house"],
                     parsed_address["street_full"])
        raise InvalidAddressError()
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address


def is_address_valid(address):
    """
    Checks that a provided AddressParser result has basic and valid information, that
    will allow us to use the address in our intents. Alexa can sometimes provide us
    with bad slot values, resulting in an invalid address.

    :param address: json object that is a result of using the AddressParer library
    :return: True if valid, False if not
    """
    return all(
        key in address
        and address[key] is not None
        for key in ("house", "street_full"))


def get_address_coordinates_from_session(mycity_request) -> dict:
    """
    Gets coordinates of the provided address from the session attributes.
    Returns None if no address is available.
    :param mycity_request: MyCityRequestDataModel for the current request
    :return dict: Dictionary containing coordinates of the address
    """
    user_address = None
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
        parsed_address = StreetAddressParser().parse(current_address)
        address = " ".join([
            parsed_address["house"],
            parsed_address["street_name"],
            parsed_address["street_type"]])
        user_address = gis_utils.geocode_address(address)

    return user_address


def get_address_coordinates_from_geolocation(mycity_request) -> dict:
    """
    Gets coordinates of the device location. Returns None if not provided
    or not accessible.
    :param mycity_request: MyCityRequestDataModel for the current request
    :return dict: Dictionary containing coordinates of the device
    """
    user_address = None
    if mycity_request.device_has_geolocation:
        if mycity_request.geolocation_permission:
            user_address = location_services_utils.convert_mycity_coordinates_to_arcgis(mycity_request)
    return user_address
