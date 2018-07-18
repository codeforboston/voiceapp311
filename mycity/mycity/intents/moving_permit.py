'''
  Moving permit Intent
  --------------------
  This intent is responsible for asking for the user's address, fetching
  the moving permits and returning the ones within a one mile range.
  
'''

import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from datetime import date
from calendar import day_name

PERMIT_INFO_URL = ('https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/' + \
                   'rest/services/Moving_Truck_Permits/FeatureServer/0')                   
DAY_OF_WEEK = day_name[date.today().weekday()]

moving_permit_data_result = {}

def get_permit_locations():
    MOVING_PERMIT_QUERY = 'Day=\'%(day)s\'' % {'day': DAY_OF_WEEK}
    print(MOVING_PERMIT_QUERY)
    
    # Result is a dictionary of moving truck permit locations
    moving_permit_data_result = gis_utils.get_features_from_feature_server(PERMIT_INFO_URL, MOVING_PERMIT_QUERY)

    # Generate unique list of food truck locations for submission to the Google Maps API
    moving_permit_unique_locations = []
    for location in moving_permit_data_result:
        print(location)
	if location["attributes"]["Loc"] not in moving_permit_unique_locations:
            moving_permit_unique_locations.append([location["attributes"]["Loc"], location["geometry"]])
	
	
    return moving_permit_unique_locations
    

def get_nearby_moving_permits():
    pass

get_permit_locations()
