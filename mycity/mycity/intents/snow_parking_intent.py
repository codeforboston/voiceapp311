"""Alexa intent used to find snow emergency parking"""

from . import intent_constants
import csv
import os
import requests
from streetaddress import StreetAddressParser
from mycity.mycity_response_data_model import MyCityResponseDataModel




# Constants 
PARKING_LOCATION_KEY = "Parking Address"
PARKING_INFO_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/' \
    + 'services/SnowParking/FeatureServer/0'
PARKING_ADDRESS_INDEX = 7


def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response information.

    :param mycity_request: MyCityRequestModel object
    :param mycity_response: MyCityResponseModel object
    :return: MyCityResponseModel object
    """
    print(
        '[method: get_snow_emergency_parking_intent]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:


        origin_address = _build_origin_address(mycity_request)


        print("Finding snow emergency parking for {}".format(origin_address))

        parking_address, driving_distance, driving_time = \
            _get_closest_parking_location(origin_address)

        if not parking_address:
            mycity_response.output_speech = "Uh oh. Something went wrong!"
        else:
            mycity_response.output_speech = \
                "The closest snow emergency parking location is at " \
                "{}. It is {} away and should take you {} to drive " \
                "there".format(parking_address, driving_distance, driving_time)

        mycity_response.should_end_session = False
    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name
    
    return mycity_response


def _build_origin_address(mycity_request):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified

    :param mycity_request: MyCityRequestDataModel object
    :return: String containing full address
    """
    print(
        '[method: _build_origin_address]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    # @todo: Repeated code -- look into using same code here and in trash intent
    address_parser = StreetAddressParser()
    current_address = \
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    parsed_address = address_parser.parse(current_address)
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address


def _get_snow_emergency_parking_location(origin_address):
