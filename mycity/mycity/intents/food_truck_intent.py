"""
Food Truck Intent

"""

import logging
import typing

from streetaddress import StreetAddressParser

from mycity.intents.custom_errors import InvalidAddressError, BadAPIResponse, MultipleAddressError
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.intents.speech_constants import food_truck_intent as speech_constants
from mycity.intents.user_address_intent import clear_address_from_mycity_object
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.utilities import datetime_utils, gis_utils
from mycity.utilities.common_types import ComplexDict
from . import intent_constants

logger = logging.getLogger(__name__)

MILE = 1600
BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/' \
               'services/food_trucks_schedule/FeatureServer/0/'
QUERY = {'where': '1=1', 'out_sr': '4326'}
DAY = datetime_utils.get_day()
FOOD_TRUCK_LIMIT = 5  # limits the number of food trucks


def add_response_text(food_trucks: typing.List[ComplexDict]) -> str:
    response = ''
    for t in food_trucks:
        response += f"{t['attributes']['Truck']} is located" \
            f" at {t['attributes']['Loc']} between " \
            f"{t['attributes']['Start_time']} and " \
            f"{t['attributes']['End_time']}, "
    return response


def get_truck_locations() -> typing.List[ComplexDict]:
    """
    Get the location of the food trucks in Boston TODAY

    :return: a list of features with unique food truck locations
    """
    trucks = gis_utils.get_features_from_feature_server(BASE_URL, QUERY)
    truck_unique_locations = []
    for t in trucks:
        if t['attributes']['Day'] == DAY:
            truck_unique_locations.append(t)
    return truck_unique_locations


def get_nearby_food_trucks(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
    """
    Gets food truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    mycity_response = MyCityResponseDataModel()

    # Get current address location
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        # Parsing street address using street-address package
        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a["house"]) + " " + str(a["street_name"]) + " " \
                  + str(a["street_type"])

        # Parsing zip code
        zip_code = str(a["other"]).zfill(5) if a["other"] else None
        zip_code_key = intent_constants.ZIP_CODE_KEY
        if zip_code is None and zip_code_key in \
                mycity_request.session_attributes:
            zip_code = mycity_request.session_attributes[zip_code_key]

        # Get user's GIS Geocode Address and list of available trucks
        usr_addr = gis_utils.geocode_address(address)
        truck_unique_locations = get_truck_locations()
        nearby_food_trucks = []

        try:
            # Loop through food truck list and search for nearby food trucks
            # limit to 5 to speed up response
            counter = 0
            for t in truck_unique_locations:
                dist = gis_utils.calculate_distance(usr_addr, t)
                if dist <= MILE:
                    nearby_food_trucks.append(t)
                    counter += 1
                    if counter == FOOD_TRUCK_LIMIT:
                        break

            count = len(nearby_food_trucks)
            if count == 0:
                mycity_response.output_speech = "I didn't find any food trucks!"

            if count == 1:
                response = f"I found {count} food truck within a mile " \
                    "from your address! "
                response += add_response_text(nearby_food_trucks)
                mycity_response.output_speech = response

            if 1 < count <= 3:
                response = f"I found {count} food trucks within a mile " \
                    "from your address! "
                response += add_response_text(nearby_food_trucks)
                mycity_response.output_speech = response

            elif count > 3:
                response = f"There are at least {count} food trucks within " \
                           f"a mile from your address! Here are the first " \
                           + str(count) + ". "
                response += add_response_text(nearby_food_trucks)
                mycity_response.output_speech = response

        except InvalidAddressError:
            address_string = address
            if zip_code:
                address_string = address_string + " with zip code {}"\
                    .format(zip_code)
            mycity_response.output_speech = \
                speech_constants.ADDRESS_NOT_FOUND.format(address_string)
            mycity_response.dialog_directive = "ElicitSlotFoodTruck"
            mycity_response.reprompt_text = None
            mycity_response.session_attributes = \
                mycity_request.session_attributes
            mycity_response.card_title = "Food Trucks"
            mycity_request = clear_address_from_mycity_object(mycity_request)
            mycity_response = clear_address_from_mycity_object(mycity_response)
            return mycity_response

        except BadAPIResponse:
            mycity_response.output_speech = \
                "Hmm something went wrong. Maybe try again?"

        except MultipleAddressError:
            mycity_response.output_speech = \
                speech_constants.MULTIPLE_ADDRESS_ERROR.format(address)
            mycity_response.dialog_directive = "ElicitSlotZipCode"

    else:
        logger.error("Error: Called food_truck_intent with no address")
        mycity_response.output_speech = "I didn't understand that address, " \
                                        "please try again"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Food Trucks"

    return mycity_response
