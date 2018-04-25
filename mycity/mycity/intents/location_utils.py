""" 
Utility functions for building addresses and finding the closest feature to an
address.
"""

from arcgis.features import FeatureLayer
from . import intent_constants
import os
import requests
from streetaddress import StreetAddressParser


###############################################################
# Constants for querying Google Maps and parsing return data  #
###############################################################


GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
DRIVING_DISTANCE_VALUE_KEY = "Driving distance"
DRIVING_DISTANCE_TEXT_KEY = "Driving distance text"
DRIVING_TIME_VALUE_KEY = "Driving time"
DRIVING_TIME_TEXT_KEY = "Driving time text"


####################
# Public functions #
####################

def build_origin_address(mcrd):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified
    :param mcrd: MyCityRequestDataModel object
    :return: String containing full address
    """
    print(
        '[method: _build_origin_address]',
        'MyCityRequestDataModel received:',
        str(mcrd)
    )

    address_parser = StreetAddressParser()
    current_address = \
        mcrd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    parsed_address = address_parser.parse(current_address)
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address


def get_closest_feature(origin, feature_address_index, 
                        feature_type, error_message, features):
    """
    Calculates the nearest feature given an origin
    :param origin: String containing starting address we calculate
    shortest distance from
    :param feature_address_index: index where address in features
    is stored
    :param feature_type: string describing the type of feature we are calculating
    the shortest distance to
    :param features: list of features fetched from FeatureServer
    :param error_message: string to print if we fail to find a closest feature
    :return: dictionary with address, distance, and driving time for
    closest feature
    """
    print(
        '[method: location_utils.get_closest_feature]',
        'origin received:',
        origin,
        'feature_address_index received:',
        feature_address_index,
        'feature_type received:',
        feature_type,
        'error_message received:',
        error_message,
        'features received:',
        features
    )

    dest_addresses = _get_dest_addresses(feature_address_index, features)
    location_driving_info = _get_driving_info(origin, feature_type, 
                                              dest_addresses)
    if len(location_driving_info) > 0:
        closest_location_info = min(location_driving_info,
                                    key= lambda x: x[DRIVING_DISTANCE_VALUE_KEY])
    else:
        print(error_message)
        closest_location_info = { feature_type: False,
                                  DRIVING_DISTANCE_TEXT_KEY: False,
                                  DRIVING_TIME_TEXT_KEY: False }
    closest_location_info = \
        _parse_closest_location_info(feature_type, closest_location_info)
    
    return closest_location_info


########################################################################
# Function that interacts with ArcGIS feature servers. Feature servers #
# serve information about locations in Boston, like locations defined  #
# as "open spaces" or snow emergency parking lots                      #
########################################################################


def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)
    :param url: url for Feature Server
    :param query: query to select features (example: "Spaces > 0")
    :return features: list of all features
    """

    print(
        '[method: location_utils.get_features_from_feature_server]',
        'url received:',
        url,
        'query received:',
        query
    )

    features = []
    f = FeatureLayer(url = url)
    feature_set = f.query(where = query)
    for feature in feature_set:
        features.append(feature.as_row[0]) # [0] = data, [1] = column names
    return features


#############################################
# Functions that interact with Google Maps  #
#############################################


def _get_driving_info(origin, feature_type, destinations):
    """
    Gets the driving info from the provided origin address to each destination
    address
    :param origin: string containing driving starting address
    :param destinations: array of address to calculate driving info from origin
    address
    :param feature_name: string representing name of this feature
    :param feature_key: string that identifies type of feature we're getting 
    directions to 
    :return driving_infos: dictionary with address, distance, and driving time from origin
    address
    """
    print(
        '[method: location_utils._get_driving_info]',
        'origin received:',
        origin,
        'feature_type received:',
        feature_type,
        'destinations received:',
        destinations
    )

    url_parameters = _setup_google_maps_query_params(origin, destinations)
    driving_directions_url = GOOGLE_MAPS_URL
    driving_infos = None
    with requests.Session() as session:
        response = session.get(driving_directions_url, params=url_parameters)
        if response.status_code == requests.codes.ok:
            all_driving_data = response.json()
            driving_infos = _parse_driving_data(all_driving_data, feature_type, destinations)
        else:
            print("Failed to get driving directions")
    return driving_infos


def _setup_google_maps_query_params(origin, destinations):
    """
    Builds a dictionary for querying Google Maps 
    :param: origin: "from" address in query
    :param: destinations: "to" addresses in query
    :return: a dictionary to use as url parameters for query
    """
    print(                      
        '[method: location_utils._setup_google_maps_query]',
        'origin received:',
        origin,
        'destinations received:',
        destinations
    )
    return {"origins": origin,
            "destinations": '|'.join(destinations),
            "key": GOOGLE_MAPS_API_KEY,
            "units": "imperial"}


##########################################################################
# Functions that parse data returned from Google Maps and FeatureServers #
##########################################################################


def _get_dest_addresses(feature_address_index, features):
    """
    :param feature_address_index: to retrieve address string in feature
    :param features: list of features retrieved from FeatureServer
    :return dest_address: list of destination addresses
    """
    dest_addresses = []

    # build array of each feature location
    for feature in features:
        dest_address = feature[feature_address_index].rstrip() # to strip \r\n 
        dest_address += " Boston, MA"
        dest_addresses.append(dest_address)
    
    return dest_addresses


def _parse_driving_data(all_driving_data, feature_type, destinations):
    """
    Retrieve data from Google Maps query into dictionary with data stored as
    key, value pairs (our keys being the constants defined at beginning of file)
    and append
    
    :param all_driving_data: JSON blob returned from Google Maps query
    :param destinations: list of destination addresses
    :param feature_type: string that identifies type of feature we're driving to
    :return driving_infos: list of dictionaries representing driving data for
    each address
    
    """
    print(
        '[method: location_utils._parse_driving_data]',
        'all_driving_data received:',
        all_driving_data,
        'feature_type received:',
        feature_type,
        'destinations received:',
        destinations
    )

    driving_infos = []
    try:
        driving_data_row = all_driving_data["rows"][0]
        for (driving_data, address) in zip(driving_data_row["elements"], 
                                           destinations):
            try:
                driving_info = {
                    DRIVING_DISTANCE_VALUE_KEY:
                        driving_data["distance"]["value"],
                    DRIVING_DISTANCE_TEXT_KEY:
                        driving_data["distance"]["text"],
                    DRIVING_TIME_VALUE_KEY:
                        driving_data["duration"]["value"],
                    DRIVING_TIME_TEXT_KEY:
                        driving_data["duration"]["text"],
                    feature_type: address}
                driving_infos.append(driving_info)
            except KeyError:
                print("Could not parse driving info {}".format(driving_data))
    except KeyError:
        pass
    finally:
        return driving_infos


def _parse_closest_location_info(feature_type, closest_location_info):
    """
    Return a sub-dictionary of the dictionary returned by the Google Maps
    estimated driving time call
    :param: closest_location_info: a dictionary with keys
    'Driving distance', 'Driving distance text', 'Driving time', 
    'Driving time text', feature_type.
    :return pruned: a dictionary with keys feature_type,
                                  DRIVING_DISTANCE_TEXT_KEY,
                                  DRIVING_TIME_TEXT_KEY
    """
    print(
        '[method: location_utils._parse_closest_location_info]',
        'feature_type received:',
        feature_type,
        'closest_location_info received:',
        closest_location_info
    )
    keys_to_keep = [feature_type, DRIVING_DISTANCE_TEXT_KEY, DRIVING_TIME_TEXT_KEY]
    return {key:closest_location_info[key] for key in keys_to_keep}
