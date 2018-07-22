"""
Utility function for building an address string from a mycity request

"""
from streetaddress import StreetAddressParser

import mycity.intents.intent_constants as intent_constants
import mycity.logger
import logging


logger = logging.getLogger(__name__)

def build_origin_address(req):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified
    
    :param req: MyCityRequestDataModel object
    :return: String containing full address
    """
    logger.debug(
        '[method: address_utils.build_origin_address]',
        'MyCityRequestDataModel received:',
        str(req)
    )

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


