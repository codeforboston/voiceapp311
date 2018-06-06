"""
Functions for Alexa responses related to food trucks
"""

<<<<<<< 6ee76a858bf67c0dbed3dbe62266631aa04028dc
import requests
import mycity.mycity.utilities.gis_utils as gis_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel
=======
#import requests
from datetime import date
from calendar import day_name
import mycity.utilities.gis_utils as gis_utils
>>>>>>> request food truck data for same day at lunch time works

"""
from mycity.mycity.mycity_response_data_model import MyCityResponseDataModel
"""

FOOD_TRUCK_FEATURE_SERVER_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/' + \
                                'food_trucks_schedule/FeatureServer/0'
DAY_OF_WEEK = day_name[date.today().weekday()]

# Note: as currently written, only fetch Lunch food trucks on that day
FOOD_TRUCK_QUERY = 'Day=\'%(day)s\' AND Time=\'%(meal)s\'' % {'day': DAY_OF_WEEK, "meal": "Lunch"}

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
