"""
Food Truck Intent
"""
import logging
import mycity.intents.speech_constants.food_truck_intent as ft_speech_constants
import mycity.intents.speech_constants.location_speech_constants as speech_const
import mycity.utilities.address_utils as address_utils
import mycity.utilities.datetime_utils as date
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.location_services_utils as location_services_utils

from mycity.intents import intent_constants
from mycity.intents.custom_errors import InvalidAddressError, BadAPIResponse
from mycity.intents.user_address_intent import \
    clear_address_from_mycity_object, request_user_address_response
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.utilities.location_services_utils import is_location_in_city


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
            f" at {t['attributes']['Location']} between {open_hours} ."
    return response


def get_truck_locations(given_address):
    """
    Get the location of the food trucks in Boston TODAY within 1 mile
    of a given_address

    :param given_address: a pair of coordinates
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

    coordinates = None
    user_address = None
    if intent_constants.CURRENT_ADDRESS_KEY not in \
            mycity_request.session_attributes:
        # If not provided, try to get the user address through
        # geolocation and device address

        coordinates = address_utils.\
            get_address_coordinates_from_geolocation(mycity_request)

        if not coordinates:
            if mycity_request.device_has_geolocation:
                return location_services_utils.\
                    request_geolocation_permission_response()

            # Try getting registered device address
            mycity_request, location_permissions = location_services_utils.\
                get_address_from_user_device(mycity_request)
            if not location_permissions:
                return location_services_utils.\
                    request_device_address_permission_response()

    if not coordinates:
        if intent_constants.CURRENT_ADDRESS_KEY \
            not in mycity_request.session_attributes:
            # We don't have coordinates or an address by now,
            # and we have all required permissions, ask the user
            return request_user_address_response(mycity_request)

        user_address = mycity_request.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY]
        coordinates = gis_utils.geocode_address(user_address)

    if not is_location_in_city(user_address, coordinates):
        mycity_response.output_speech = speech_const.NOT_IN_BOSTON_SPEECH
        mycity_response.should_end_session = True
        mycity_response.card_title = CARD_TITLE
        return mycity_response

    # Get list of available trucks
    truck_unique_locations = get_truck_locations(coordinates)

    # Create custom response based on number of trucks returned
    try:
        if len(truck_unique_locations) == 0:
            mycity_response.output_speech = "I didn't find any food " \
                                            "trucks near you!"

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
        mycity_response.output_speech = \
            ft_speech_constants.ADDRESS_NOT_FOUND.format("that address")
        mycity_response.dialog_directive = "ElicitSlotFoodTruck"
        mycity_response.reprompt_text = None
        mycity_response.session_attributes = \
            mycity_request.session_attributes
        mycity_response.card_title = CARD_TITLE
        mycity_request = clear_address_from_mycity_object(mycity_request)
        mycity_response = clear_address_from_mycity_object(mycity_response)
        mycity_response.should_end_session = True
        return mycity_response

    except BadAPIResponse:
        mycity_response.output_speech = \
            "Hmm something went wrong. Maybe try again?"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE
    mycity_response.should_end_session = True

    return mycity_response
