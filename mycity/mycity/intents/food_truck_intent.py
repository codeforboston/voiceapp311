"""
Functions for Alexa responses related to food trucks
"""

import requests
import mycity.mycity.utilities.gis_utils as gis_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel

"""
from mycity.mycity.mycity_response_data_model import MyCityResponseDataModel
"""

FOOD_TRUCK_FEATURE_SERVER_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/' + \
                                'food_trucks_schedule/FeatureServer/0'
FOOD_TRUCK_QUERY = '1=1'

food_truck_data_result = gis_utils.get_features_from_feature_server(FOOD_TRUCK_FEATURE_SERVER_URL, FOOD_TRUCK_QUERY)

print(food_truck_data_result)



def get_nearby_food_trucks(mycity_request):
    """
    Gets food truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """

    mycity_response = MyCityResponseDataModel()
    mycity_response.output_speech = "Chicken and rice guys!!!"
    return mycity_response
