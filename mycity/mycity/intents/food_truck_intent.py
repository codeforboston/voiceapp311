"""
Food Truck Intent
"""
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.datetime_utils as date
import mycity.intents.speech_constants.food_truck_intent as speech_constants
import logging
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.intents.user_address_intent import clear_address_from_mycity_object
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
from .custom_errors import \
    InvalidAddressError, BadAPIResponse, MultipleAddressError
from . import intent_constants

logger = logging.getLogger(__name__)

MILE = 1600
BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/' \
               'services/food_truck_schedule/FeatureServer/0/'
DAY = date.get_day()
FOOD_TRUCK_LIMIT = 5  # limits the number of food trucks
CARD_TITLE = "Food Trucks"
QUERY = {
    "distance": "1",
    "inSR": "4326",
    "outSR": "4326",
    "f": "json",
    "outfields": "*",
    "units": "esriSRUnit_StatuteMile",
    "geometryType": "esriGeometryPoint"
}


def add_response_text(food_trucks):
    length = min(FOOD_TRUCK_LIMIT, len(food_trucks))
    response = ''
    for x in range(length):
        t = food_trucks[x]
        open_hours = str(t['attributes']['Hours']).replace("-", "and")
        response += f"{t['attributes']['Truck']} is located" \
            f" at {t['attributes']['Location']} between {open_hours},"
    return response


def get_truck_locations(given_address):
    """
    Get the location of the food trucks in Boston TODAY within 1 mile
    of a given_address

    :return: a list of features with unique food truck locations
    """
    formatted_address = '{x_coordinate}, {y_coordinate}'.format(
        x_coordinate=given_address['x'],
        y_coordinate=given_address['y']
    )
    QUERY["geometry"] = formatted_address

    trucks = gis_utils.get_features_from_feature_server(BASE_URL, QUERY)
    truck_unique_locations = []
    for t in trucks:
        if t['attributes']['Day'] == DAY:
            truck_unique_locations.append(t)
    return truck_unique_locations


def get_nearby_food_trucks(mycity_request):
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
        truck_unique_locations = get_truck_locations(usr_addr)

        # Create custom response based on number of trucks returned
        try:
            if len(truck_unique_locations) == 0:
                mycity_response.output_speech = "I didn't find any food trucks!"

            if len(truck_unique_locations) == 1:
                response = f"I found {len(truck_unique_locations)} food " \
                           f"truck within a mile from your address! "
                response += add_response_text(truck_unique_locations)
                mycity_response.output_speech = response

            if 1 < len(truck_unique_locations) <= 3:
                response = f"I found {len(truck_unique_locations)} food " \
                           f"trucks within a mile from your address! "
                response += add_response_text(truck_unique_locations)
                mycity_response.output_speech = response

            if len(truck_unique_locations) > 3:
                response = f"There are at least {len(truck_unique_locations)}" \
                           f" food trucks within a mile from your " \
                           f"address! Here are the first five. "
                response += add_response_text(truck_unique_locations)
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
            mycity_response.card_title = CARD_TITLE
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
    mycity_response.card_title = CARD_TITLE

    return mycity_response
