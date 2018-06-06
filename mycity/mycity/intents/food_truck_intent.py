"""
Functions for Alexa responses related to food trucks
"""

import requests
import mycity.utilities.gis_utils as gis_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel
from datetime import date
from calendar import day_name

FOOD_TRUCK_FEATURE_SERVER_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/' + \
                                'food_trucks_schedule/FeatureServer/0'
DAY_OF_WEEK = day_name[date.today().weekday()]

# Note: as currently written, only fetch Lunch food trucks on that day
FOOD_TRUCK_QUERY = 'Day=\'%(day)s\' AND Time=\'%(meal)s\'' % {'day': DAY_OF_WEEK, "meal": "Lunch"}

food_truck_data_result = gis_utils.get_features_from_feature_server(FOOD_TRUCK_FEATURE_SERVER_URL, FOOD_TRUCK_QUERY)

# Generate unique list of food truck locations for submission to the Google Maps API
truck_unique_locations = []
for truck in food_truck_data_result:
  if truck["attributes"]["Loc"] not in truck_unique_locations:
    truck_unique_locations.append([truck["attributes"]["Loc"], truck["geometry"]])

print(truck_unique_locations)

# Build JSON object for Google Maps request. Submit locations to Google Maps API to get distances
# Parse Google Maps API response to get 1 closest location.
# Distill food truck list to provide food trucks at the 1 closest location

def get_nearby_food_trucks(mycity_request):
    """
    Gets food truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """

    mycity_response = MyCityResponseDataModel()
    mycity_response.output_speech = "Chicken and rice guys!!!"
    return mycity_response
