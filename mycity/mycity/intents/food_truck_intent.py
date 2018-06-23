"""
Functions for Alexa responses related to food trucks
"""

import requests
import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from datetime import date
from calendar import day_name

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
            truck_unique_locations.append([truck["attributes"]["Loc"], truck["geometry"]])

    return truck_unique_locations

def get_nearby_food_trucks(mycity_request):
    """
    Gets food truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """

    # Get current address location
    # TODO: this block is copy/pasted from trash_intent.py, should refactor
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name'])

        truck_unique_locations = get_truck_locations()

        try:
            #TODO: currently just gets distance to first location given (??). Should loop through or modify get_closest_feature to return closest location in list
            closest_truck = gis_utils.get_closest_feature(origin=address,
                                                          feature_address_index=1,
                                                          feature_type='Food truck list',
                                                          error_message='Unable to find food trucks closest to you',
                                                          features=truck_unique_locations)
            print(closest_truck_location)

            #TODO: take this location and get all food trucks at this location
        except:
            print('ERROR: unable to find closest food truck location to you')

    mycity_response = MyCityResponseDataModel()
    mycity_response.output_speech = "Chicken and rice guys!!!"
    return mycity_response
