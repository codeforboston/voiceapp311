"""
Utility function for building an address string from a mycity request

"""

import logging

from streetaddress import StreetAddressParser

from mycity.intents import intent_constants
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.utilities.common_types import ComplexDict

logger = logging.getLogger(__name__)


def build_origin_address(req: MyCityRequestDataModel) -> str:
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
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address

def is_address_valid(address: ComplexDict) -> bool:
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
