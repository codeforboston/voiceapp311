"""
Functions for Alexa responses related to food trucks
"""
import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
from datetime import date
from calendar import day_name
import logging
from pyproj import Proj, transform
from .custom_errors import \
    InvalidAddressError, BadAPIResponse

logger = logging.getLogger(__name__)
MERCATOR = 'epsg:3857'  # defines pseudo-mercator coordinate system, i.e., it uses X,Y instead of lat,long
                        # (ref.: https://epsg.io/3857)
GEODETIC = 'epsg:4326'  # defines geodetic coordinate system, i.e., lat, long. (ref.: https://epsg.io/4326)
MILE_IN_KILOMETERS = 1.6


def convert_xy_to_lat_long(coordinates):
    """
    Some datasets use (x,y) coordinates to form map projection. This method converts it to lat and long
    :param coordinates: a list with X and Y
    :return: a list of Lat and Long
    """
    inProj = Proj(init=MERCATOR)
    outProj = Proj(init=GEODETIC)
    return [coordinate for coordinate in transform(inProj, outProj, coordinates[0], coordinates[1])]


def get_truck_locations():
    """
    Dynamically queries arcgis data and returns a list of food truck locations in Boston
    TODO: add food truck name as optional filter

    :return: list of lists containing location name, dict ofGPS coordinates in value
      for example: [['Sumner Street', {'x': -7908107.9125, 'y': 5216395.7579}],
      ['Boylston/Clarendon by Trinity Church', {'x': -7912059.823100001, 'y': 5213652.076399997}]]
    """
    FOOD_TRUCK_FEATURE_SERVER_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/' + \
                                'food_trucks_schedule/FeatureServer/0'
    DAY_OF_WEEK = day_name[date.today().weekday()]

    # Note: as currently written, only fetch Lunch food trucks on that day
    FOOD_TRUCK_QUERY = 'Day=\'%(day)s\' AND Time=\'%(meal)s\'' % {'day': DAY_OF_WEEK, "meal": "Lunch"}

    # Result is a dictionary of food truck locations
    food_truck_data_result = gis_utils.get_features_from_feature_server(FOOD_TRUCK_FEATURE_SERVER_URL, FOOD_TRUCK_QUERY)

    # Generate unique list of food truck locations for submission to the Google Maps API
    truck_unique_locations = []
    for truck in food_truck_data_result:
        if truck["attributes"]["Loc"] not in truck_unique_locations:
            truck_unique_locations.append([truck["attributes"]["Loc"], truck["geometry"]])

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
        address = str(a['house']) + " " + str(a['street_name']) + " " + str(a['street_type'])

        # Convert address to X, Y
        usr_addr_xy = gis_utils.geocode_address(address)

        truck_unique_locations = get_truck_locations()

        count = 0
        try:
            for location in truck_unique_locations:
                permit_xy = list(location[1].values())
                permit_xy = convert_xy_to_lat_long(permit_xy)
                dist = gis_utils.calculate_distance(usr_addr_xy, permit_xy)
                if dist <= MILE_IN_KILOMETERS:
                    count += 1

            if count == 1:
                mycity_response.output_speech = "I found {} food truck within a mile \
                                                from your address.".format(count)
            elif count == 2:
                mycity_response.output_speech = "I found {} food trucks within a mile \
                                                from your address.".format(count)
            else:
                mycity_response.output_speech = "I found {} food trucks within a mile \
                                                 from your address. Would you like to hear" \
                                                " the first three?".format(count)
        except InvalidAddressError:
            address_string = address

            mycity_response.output_speech = \
                "I can't seem to find {}. Try another address" \
                    .format(address_string)
            mycity_response.reprompt_text = None
            mycity_response.session_attributes = mycity_request.session_attributes
            mycity_response.card_title = "Food Trucks"
            mycity_request = clear_address_from_mycity_object(mycity_request)
            mycity_response = clear_address_from_mycity_object(mycity_response)
            return mycity_response

        except BadAPIResponse:
            mycity_response.output_speech = \
                "Hmm something went wrong. Maybe try again?"

    else:
        logger.error("Error: Called food_truck_intent with no address")
        mycity_response.output_speech = "I didn't understand that address, please try again"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Food Trucks"

    return mycity_response
