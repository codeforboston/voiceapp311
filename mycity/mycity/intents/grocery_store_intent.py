"""
Grocery Store Intent
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

BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/' \
           'services/Supermarkets_GroceryStores/FeatureServer/0'
DAY = date.get_day()
CARD_TITLE = "Grocery Store"
QUERY = {
    "distance": "1",
    "inSR": "4326",
    "outSR": "4326",
    "f": "json",
    "outfields": "*",
    "units": "esriSRUnit_StatuteMile",
    "geometryType": "esriGeometryPoint"
}


def add_response_text(features):
    """
    Iterated through the list of features, extracts the useful fields, and
    creates the response text.
    :param features:
    :return: response :string
    """
    response = ''
    for t in features:
        response += f"{t['attributes']['Store']}" \
            f" in {t['attributes']['Neighborho']} is located at " \
            f"{t['attributes']['Address']}. "
    return response


def get_grocery_grocery_stores(address_of_interest):
    """
    Gets the grocery store location within a mile from a given address
    :return: a list of features with unique grocery stores
    """

    formatted_address = '{x_coordinate}, {y_coordinate}'.format(
        x_coordinate=address_of_interest['x'],
        y_coordinate=address_of_interest['y']
    )
    QUERY["geometry"] = formatted_address

    grocery_stores = gis_utils.get_features_from_feature_server(BASE_URL, QUERY)
    return grocery_stores


def get_nearby_grocery_stores(mycity_request):
    """
    Get grocery stores near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    mycity_response = MyCityResponseDataModel()

    coordinates = None
    # Get current address location
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

        # Get user's address and get grocery stores
        nearby_grocery_stores = get_grocery_grocery_stores(coordinates)

        try:
            if len(nearby_grocery_stores):
                response = 'The following markets are located within a mile ' \
                           'from you. '
                response += add_response_text(nearby_grocery_stores)
                mycity_response.output_speech = response
            else:
                response = 'I did not find any grocery stores within a mile ' \
                           'from your address.'
                mycity_response.output_speech = response

        except InvalidAddressError:
            mycity_response.output_speech = \
                ft_speech_constants.ADDRESS_NOT_FOUND.format("that address")
            mycity_response.dialog_directive = "ElicitSlotGroceryStore"
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

    else:
        logger.error("Error: Called grocery_store_intent with no address")
        mycity_response.output_speech = "I didn't understand that address, " \
                                        "please try again"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE

    return mycity_response
