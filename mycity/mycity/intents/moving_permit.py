'''
  Moving permit Intent
  --------------------
  This intent is responsible for asking for the user's address, fetching
  the moving permits and returning the ones within a one mile range.
  
  To run this file directly on the intents folder, use the following
  $ PYTHONPATH=../../ python3 moving_permit.py
  
  which will tell the interpreter that the mycity packacge is located
  two levels above.
'''

import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel

from datetime import datetime

PERMIT_INFO_URL = ('https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/' + \
                   'rest/services/Moving_Truck_Permits/FeatureServer/0')                   
DAY_OF_WEEK = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
STATUS = 'OPEN'

moving_permit_data_result = {}

def get_permit_locations():
    """
    Queries arcgis data and returns a list of moving permit locations

    :return: list of lists containing location name, dict ofGPS coordinates in value
      for example: [['Sumner Street', {'x': -7908107.9125, 'y': 5216395.7579}],
      ['Boylston/Clarendon by Trinity Church', {'x': -7912059.823100001, 'y': 5213652.076399997}]]
    """
    MOVING_PERMIT_QUERY = 'Status=\'%(status)s\'' % {"status": STATUS}
    print('Querying... ' + str(MOVING_PERMIT_QUERY) + '\n')
    
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
