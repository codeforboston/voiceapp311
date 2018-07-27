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
from streetaddress import StreetAddressParser


PERMIT_INFO_URL = ('https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/' + \
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
                moving_permit_unique_locations.append([location['attributes']['PermitNumb'], \
                                                       location['geometry']])
            except:
                #print('PermitNumb: ' + str(location['attributes']['PermitNumb']) + ' has no geometry')
                pass
    
    return moving_permit_unique_locations
    

def get_nearby_moving_permits(mycity_request):
    """
    Gets moving truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    
    print(
        '[module: MovingPermitsIntent]',
        '[method: get_permit_locations]',
        'MyCityRequestDataModel received: ',
        str(mycity_request)
    )
    
    # TODO: this block is copy/pasted from trash_intent.py, should refactor
    
    # Get user's address
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name'])
        
        # Get moving permit locations
        moving_permit_unique_locations = get_permit_locations()
        
        try:
            closest_trucks = gis_utils.get_closest_feature(origin=address,
                                                           feature_address_index=1,
                                                           feature_type='Moving truck list',
                                                           error_message='Unable to find moving trucks closest to you',
                                                           features=moving_permit_unique_locations)
            print(closest_trucks)

        except:
            mycity_response.output_speech = "There was an issue retrieving the data"
            print('ERROR: unable to find nearby moving trucks')
            

    mycity_response = MyCityResponseDataModel()
    mycity_response.output_speech = "I found {} moving permits within a mile from your address."\
                                    .format(len(closest_trucks))
    print(
        '[module: MovingPermitsIntent]',
        '[method: get_permit_locations]',
        'MyCityResponseDataModel: ',
        str(mycity_request)
    )
    
    return mycity_response
