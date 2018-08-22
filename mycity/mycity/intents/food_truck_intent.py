"""
Functions for Alexa responses related to food trucks
"""

import requests
import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
from datetime import date
from calendar import day_name
import logging

logger = logging.getLogger(__name__)

# Note: food truck data result is queried twice, for unique locations, then for all trucks at nearest location,
#   so it needs to be accessed outside of get_truck_locations()
food_truck_data_result = {}

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
            print(truck)
            print('\n')
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
    # TODO: this block is copy/pasted from trash_intent.py, should refactor
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name']) + " " + str(a['street_type'])

        # Convert address to X, Y
        usr_addr_xy = gis_utils.geocode_address(address)
        print('User\'s address: ' + str(usr_addr_xy))

        truck_unique_locations = get_truck_locations()

        count = 0
        try:
            for i in range(len(truck_unique_locations)):
                permit_xy = list(truck_unique_locations[i][1].values())
                print('Permit location: ' + str(permit_xy))

                dist = gis_utils.calculate_distance(usr_addr_xy, permit_xy)
                print('Distance to fod truck: ' + str(dist))
                if dist <= 1.6:  # in km
                    count += 1
            mycity_response.output_speech = "I found {} food trucks within a mile from your \
                                                     address.".format(count)
        except:
            mycity_response.output_speech = "There was an issue processing the data"
            logger.error('ERROR: unable to find nearby moving trucks')

    return mycity_response

print(get_truck_locations())
