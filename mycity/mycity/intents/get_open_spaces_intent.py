"""
Intent for finding the nearest open space (playground, ball field, etc.) to a
given address

"""

from . import intent_constants
import location_utils

# Constants
OPEN_SPACES_LOCATION_KEY = "Open Space Address"
OPEN_SPACES_INFO_URL = "http://gis.cityofboston.gov/arcgis/rest/" \
        + "services/EnvironmentEnergy/OpenData/MapServer/7"
OPEN_SPACES_ADDRESS_INDEX = 7


def get_open_spaces_intent(mdc):
    """
    Populate MyCityDataModel with information about nearest open spaces,
    an open space being a park, playground, etc.

    :param mcd: a MyCityDataModel
    :return mcd: the MyCityDataModel populated with a new speech response

    """
    print(
        '[method: get_open_spaces_intent]',
        'MyCityDataModel received:',
        str(mcd)
    )

    if intent_constants.CURRENT_ADDRESS_KEY in mcd.session_attributes:
        origin_address = location_utils.build_origin_address(mcd)
        print("Finding a nearby open space for {}".format(origin_address))
        open_space_address, driving_distance, driving_time = \
            _get_closest_open_space(origin_adress)

        if not open_space_address:
            mcd.output_speech = "Uh oh. Something went wrong!"
        else:
            mcd.output_speech = \
                ("The closest open space is at {}. "
                "It is {} away and should take you {} to drive "
                "there").format(open_space_address, driving_distance, 
                               driving_time)
        mcd.should_end_session = False
    else:
        print("Error: Called open_spaces_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mcd.reprompt_text = None
    return mcd
    

def _get_closest_open_space(origin_address):
 """
    Calculates the address, distance, and driving time for the closest
    open space.

    :param origin_address: string containing the address used to find the
    closest emergency parking location
    :return: parking address, distance, and driving time
    """
    print(
        '[method: _get_closest_open_space]',
        'origin_address received:',
        origin_address
        )
    error_message = "Didn't find any open spaces" 
    all_open_spaces = _get_open_spaces()
    closest_open_space = \
        location_utils.get_closest_feature(origin_address,
                                           OPEN_SPACES_ADDRESS_INDEX,
                                           OPEN_SPACES_LOCATION_KEY,
                                           error_message,
                                           all_open_spaces)
    return closest_open_space


def _get_all_open_spaces():
    """
    Gets all open spaces from City's FeatureServer for recreational areas.

    :return: array of emergency parking info as provided from City's ArcGIS
    Feature Server for snow parking lots
    """

    print(
        '[method: _get_all_open_spaces]'
    )     
    query = "1=1"
    return location_utils.get_features_from_feature_server(OPEN_SPACES_INFO_URL, 
                                                           query)





