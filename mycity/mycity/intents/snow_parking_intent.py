"""Alexa intent used to find snow emergency parking"""

import intent_constants
import location_utils




# Constants 
PARKING_LOCATION_KEY = "Parking Address"
PARKING_INFO_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/' \
    + 'services/SnowParking/FeatureServer/0'
# todo: modify location_utils functions to keep name of parking lot available
# for concating to speech output 
PARKING_NAME_INDEX = 6
PARKING_ADDRESS_INDEX = 7


def get_snow_emergency_parking_intent(mcd):
    """
    Populate MyCityDataModel with snow emergency parking response information.

    :param mcd:
    :return:
    """
    print(
        '[method: get_snow_emergency_parking_intent]',
        'MyCityDataModel received:',
        str(mcd)
    )

    if intent_constants.CURRENT_ADDRESS_KEY in mcd.session_attributes:

        origin_address = location_utils.build_origin_address(mcd)

        print("Finding snow emergency parking for {}".format(origin_address))

        parking_address, driving_distance, driving_time = \
            _get_closest_parking_location(origin_address)

        if not parking_address:
            mcd.output_speech = "Uh oh. Something went wrong!"
        else:
            mcd.output_speech = \
                "The closest snow emergency parking location is at " \
                "{}. It is {} away and should take you {} to drive " \
                "there".format(parking_address, driving_distance, driving_time)

        mcd.should_end_session = False
    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mcd.reprompt_text = None
    return mcd



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
