"""
  Moving permit Intent
  --------------------
  This intent is responsible for asking for the user's address, fetching
  the moving permits and returning the ones within a one mile range.
  
  To run this file directly on the intents folder, use the following
  $ PYTHONPATH=../../ python3 moving_permit.py
  
  which will tell the interpreter that the mycity packacge is located
  two levels above.
"""

import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
import mycity.logger
import logging

logger = logging.getLogger(__name__)
PERMIT_INFO_URL = ('https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/' +
                   'rest/services/Moving_Truck_Permits/FeatureServer/0')                   
STATUS = 'OPEN'
moving_permit_data_result = {}


def get_permit_locations():
    """
    Queries arcgis data and returns a list of moving permit locations

    :return: list of lists containing the permit number and a dict of 
             GPS coordinates in value.
      for example: [['OCCU-752664', {'x': -71.10079000035819, 'y': 42.32857000010546}], 
                    ['OCCU-752685', {'x': -71.11067100006659, 'y': 42.32055099992874}]]
    """
    
    MOVING_PERMIT_QUERY = 'Status=\'%(status)s\'' % {'status': STATUS}
    
    # Result is a dictionary of moving truck permit
    moving_permit_data_result = gis_utils.get_features_from_feature_server(PERMIT_INFO_URL, MOVING_PERMIT_QUERY)

    # Generate unique list of moving truck locations for submission to the Google Maps API
    moving_permit_unique_locations = []
    for location in moving_permit_data_result:
        if location['attributes']['PermitNumb'] not in moving_permit_unique_locations:
            # this try block is necessary because some permits don't have geometry!
            try:
                moving_permit_unique_locations.append([location['attributes']['PermitNumb'],
                                                       location['geometry']])
            except:
                #print('Permit has no geometry')
                pass
    
    return moving_permit_unique_locations
    

def get_nearby_moving_permits(mycity_request):
    """
    Gets moving truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    logger.debug('[module: MovingPermitsIntent]' +
                 '[method: get_permit_locations]' +
                 'MyCityRequestDataModel received: ' +
                 str(mycity_request))

    mycity_response = MyCityResponseDataModel()
    
    # Get user's address
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name']) + " " + str(a['street_type'])

        # Convert address to X, Y
        usr_addr_xy = gis_utils.geocode_address(address)
        
        # Get list of lists of moving permit ID and locations
        moving_permit_unique_locations = get_permit_locations()

        count = 0
        try:
            for i in range(len(moving_permit_unique_locations)):
                permit_xy = list(moving_permit_unique_locations[i][1].values())
                dist = gis_utils.calculate_distance(usr_addr_xy, permit_xy)
                if dist <= 0.8:
                    count += 1
            mycity_response.output_speech = "I found {} active moving permits within half a mile from your \
                                             address.".format(count)

        except:
            mycity_response.output_speech = "There was an issue processing the data"
            logger.error('ERROR: unable to find nearby moving trucks')
    
    return mycity_response
