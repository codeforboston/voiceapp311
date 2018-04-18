""" 
Common code used across intents to build a string using the MyCity object to
represent the user's address
"""

from . import intent_constants
from streetaddress import StreetAddressParser


def build_origin_address(mcd):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified

    :param mcd: MyCityDataModel object
    :return: String containing full address
    """
    print(
        '[method: _build_origin_address]',
        'MyCityDataModel received:',
        str(mcd)
    )

    address_parser = StreetAddressParser()
    current_address = \
        mcd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    parsed_address = address_parser.parse(current_address)
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address



