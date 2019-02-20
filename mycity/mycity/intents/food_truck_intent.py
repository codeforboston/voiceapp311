"""
Food Truck Intent

"""
import mycity.utilities.gis_utils as gis_utils
import mycity.intents.speech_constants.food_truck_intent as speech_constants
import logging
import requests

from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.intents.user_address_intent import clear_address_from_mycity_object
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
import datetime
from .custom_errors import \
    InvalidAddressError, BadAPIResponse, MultipleAddressError
from . import intent_constants

logger = logging.getLogger(__name__)

MILE_IN_KILOMETERS = 1.6


def get_truck_locations():
    """
    Get the location of the food trucks in Boston

    :return: JSON object containing API parameters in the folllwing format:
    {
        'attributes': {'CreationDate': 1520268574231,
                       'Creator': '143525_boston',
                       'Day': 'Wednesday',
                       'EditDate': 1520268574231,
                       'Editor': '143525_boston',
                       'End_time': '3:00:00 PM',
                       'FID': 10,
                       'GlobalID': 'd4a84cb9-8685-461a-ab5e-a19260656933',
                       'Hours': '11 a.m. - 3 p.m.',
                       'Link': 'http://www.morockinfusion.com/',
                       'Loc': 'Chinatown Park',
                       'Management': 'Rose Kennedy Greenway Conservancy',
                       'Notes': ' ',
                       'POINT_X': -7910324.35486,
                       'POINT_Y': 5213745.7545,
                       'Site_num': 0,
                       'Start_time': '11:00:00 AM',
                       'Time': 'Lunch',
                       'Title': 'Greenway',
                       'Truck': "Mo'Rockin Fusion"},
       'geometry': {'x': -71.05965270349564, 'y': 42.351281064296}
    }
    """
    base_url = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/' \
               'services/food_trucks_schedule/FeatureServer/0/query'
    day_of_week = "Day='" + datetime.datetime.today().strftime('%A') + "' "
    url_params = {
        "f": "json",
        "outFields": "*",
        "outSR": "4326",
        "returnGeometry": "true",
        "where": day_of_week
    }
    logger.debug("Requesting data from ArcGIS server!")
    food_truck_data_result = requests.get(base_url, url_params)
    response_code = food_truck_data_result.status_code
    logger.debug("Got response code: " + str(response_code))
    if response_code != requests.codes.ok:
        logger.debug('HTTP Error: '.format(response_code))
        return {}

    print(food_truck_data_result)

    # Generate unique list of food truck locations
    # to send to the Google Maps API
    trucks = food_truck_data_result.json()['features']
    truck_unique_locations = []
    for truck in trucks:
        if truck["attributes"]["Loc"] not in truck_unique_locations:
            truck_unique_locations.append([truck["geometry"],
                                           truck["attributes"]["Truck"],
                                           truck["attributes"]["Loc"],
                                           truck["attributes"]["Title"],
                                           truck["attributes"]["Start_time"],
                                           truck["attributes"]["End_time"]])
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

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name']) + " " \
                  + str(a['street_type'])
        zip_code = str(a["other"]).zfill(5) if a["other"] else None

        zip_code_key = intent_constants.ZIP_CODE_KEY
        if zip_code is None and zip_code_key in \
                mycity_request.session_attributes:
            zip_code = mycity_request.session_attributes[zip_code_key]

        usr_addr = gis_utils.geocode_address(address)
        truck_unique_locations = get_truck_locations()
        nearby_food_trucks = []
        try:
            for location in truck_unique_locations:
                truck_lat_lon = list(location[0].values())
                dist = gis_utils.calculate_distance(usr_addr, truck_lat_lon)

                if dist <= MILE_IN_KILOMETERS:
                    nearby_food_trucks.append(location)
                else:
                    continue

            count = len(nearby_food_trucks)
            if count == 0:
                mycity_response.output_speech = "I didn't find any food trucks!"

            if 0 < count <= 3:
                response = f"I found {count} food trucks within a mile " \
                    "from your address! "
                for i in range(count):
                    response += f"{nearby_food_trucks[0][1]} is located at " \
                        f"{nearby_food_trucks[i][2]} and " \
                        f"{nearby_food_trucks[i][3]}, from " \
                        f"{nearby_food_trucks[i][4]} to " \
                        f"{nearby_food_trucks[i][5]}, "
                mycity_response.output_speech = response

            elif count > 3:
                response = f"I found {count} food trucks within a mile " \
                    "from your address! Here are the first three: "
                for i in range(3):
                    response += f"{nearby_food_trucks[i][1]} is located at "\
                        f"{nearby_food_trucks[i][2]} and " \
                        f"{nearby_food_trucks[i][3]}, from " \
                        f"{nearby_food_trucks[i][4]} to " \
                        f"{nearby_food_trucks[i][5]}, "
                response += "Would you like to hear more?"
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
