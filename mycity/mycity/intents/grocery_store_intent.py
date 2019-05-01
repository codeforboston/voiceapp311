"""
Grocery Store Intent
"""
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.datetime_utils as date
import logging
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from . import intent_constants
from streetaddress import StreetAddressParser
from .custom_errors import \
    InvalidAddressError, BadAPIResponse, MultipleAddressError
import mycity.intents.speech_constants.food_truck_intent as speech_constants
from mycity.intents.user_address_intent import clear_address_from_mycity_object

logger = logging.getLogger(__name__)

BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/' \
           'services/Supermarkets_GroceryStores/FeatureServer/0'
QUERY = {
    "distance": "1",
    "inSR": "4326",
    "outSR": "4326",
    "f": "json",
    "outfields": "*",
    "units": "esriSRUnit_StatuteMile",
    "geometryType": "esriGeometryPoint"
}
DAY = date.get_day()
CARD_TITLE = "Grocery Stores"


def add_response_text(features):
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

        # Get user's address and get grocery stores
        usr_addr = gis_utils.geocode_address(address)
        nearby_grocery_stores = get_grocery_grocery_stores(usr_addr)

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
        logger.error("Error: Called grocery_store_intent with no address")
        mycity_response.output_speech = "I didn't understand that address, " \
                                        "please try again"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Grocery Store"

    return mycity_response
