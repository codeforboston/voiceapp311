"""
Intent for finding the nearest open space (playground, ball field, etc.) to a
given address

"""

from . import intent_constants
from . import location_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel


# Constants
OPEN_SPACES_LOCATION_KEY = "Open Space Address"
OPEN_SPACES_INFO_URL = "http://gis.cityofboston.gov/arcgis/rest/" \
        + "services/EnvironmentEnergy/OpenData/MapServer/7"
# todo: it would be good if we could preserve the name of an open 
# space while looking up driving directions
OPEN_SPACES_NAME_INDEX = 1
OPEN_SPACES_ADDRESS_INDEX = 7


def get_open_spaces_intent(mycity_request):
    """
    Populate MyCityRequestDataModel with information about nearest open spaces,
    an open space being a park, playground, etc.

    :param mycity_request: a MyCityDataModel
    :return mcd: the MyCityDataModel populated with a new speech response
    """
    print(
        '[method: get_open_spaces_intent]',
        'MyCityDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        origin_address = location_utils.build_origin_address(mycity_response)
        print("Finding a nearby open space for {}".format(origin_address))
        closest_open_space = _get_closest_open_space(origin_address)
        open_space_address = closest_open_space[OPEN_SPACES_LOCATION_KEY]
        driving_distance = closest_open_space[location_utils.DRIVING_DISTANCE_TEXT_KEY]
        driving_time = closest_open_spaces[location_utils.DRIVING_TIME_TEXT_KEY]

        if not open_space_address:
            mycity_response.output_speech = "Uh oh. Something went wrong!"
        else:
            mycity_response.output_speech = \
                ("The closest public park or playground is at {}. "
                "It is {} away and should take you {} to drive "
                "there").format(open_space_address, driving_distance, 
                               driving_time)
        mycity_response.should_end_session = False
    else:
        print("Error: Called open_spaces_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name

    return mycity_response
    

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
    query = "Ownership not like 'Private'"  # exclude private spaces 
    return location_utils.get_features_from_feature_server(OPEN_SPACES_INFO_URL, 
                                                           query)





