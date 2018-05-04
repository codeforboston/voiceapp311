"""Alexa intent used to find snow emergency parking"""


from . import intent_constants
from . import location_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel




# Constants 
PARKING_LOCATION_KEY = "Parking Address"
PARKING_INFO_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/' \
    + 'services/SnowParking/FeatureServer/0'
# TODO: modify location_utils functions to keep name of parking lot available
# for concating to speech output 
PARKING_NAME_INDEX = 6
PARKING_ADDRESS_INDEX = 7


def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response information.

    :param mycity_request: MyCityRequestModel object
    :param mycity_response: MyCityResponseModel object
    :return: MyCityResponseModel object
    """
    print(
        '[method: get_snow_emergency_parking_intent]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        origin_address = location_utils.build_origin_address(mycity_request) 

        print("Finding snow emergency parking for {}".format(origin_address))
        closest_parking_lot = _get_closest_parking_location(origin_address)
        parking_address = closest_parking_lot[PARKING_LOCATION_KEY]
        driving_distance = closest_parking_lot[location_utils.DRIVING_DISTANCE_TEXT_KEY]
        driving_time = closest_parking_lot[location_utils.DRIVING_TIME_TEXT_KEY]

        if not parking_address:
            mycity_response.output_speech = "Uh oh. Something went wrong!"
        else:
            mycity_response.output_speech = \
                "The closest snow emergency parking location is at " \
                "{}. It is {} away and should take you {} to drive " \
                "there".format(parking_address, driving_distance, driving_time)

        mycity_response.should_end_session = False
    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name
    
    return mycity_response




def _get_closest_parking_location(origin_address):
    """
    Calculates the address, distance, and driving time for the closest snow
    emergency parking location.

    :param origin_address: string containing the address used to find the
    closest emergency parking location
    :return: parking address, distance, and driving time
    """
    print(
        '[method: _get_snow_emergency_parking_location]',
        'origin_address received:',
        origin_address
    )
    error_message = "Didn't find any parking locations"
    parking_data = _get_emergency_parking_data()
    closest_parking_lot = \
        location_utils.get_closest_feature(origin_address,
                                           PARKING_ADDRESS_INDEX,
                                           PARKING_LOCATION_KEY,
                                           error_message,
                                           parking_data)
    return closest_parking_lot

                                                             
def _get_emergency_parking_data():
    """
    Gets the emergency parking info from Boston Data

    :return: array of emergency parking info as provided from City's ArcGIS
    Feature Server for snow parking lots
    """
    print(
        '[method: _get_emergency_parking_data]'
    )     
    query = "Spaces > 0"
    return location_utils.get_features_from_feature_server(PARKING_INFO_URL, 
                                                           query)
