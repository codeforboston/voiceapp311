"""
Utilty functions that interact with ArcGIS Feature Servers

NOTE: Intents that query FeatureServers may fail because AWS will
kill any computation that takes longer than 3 secs.

"""

from arcgis.features import FeatureLayer

import mycity.utilities.google_maps_utils as g_maps_utils


def get_closest_feature(origin, feature_address_index, 
                        feature_type, error_message, features):
    """
    Calculates the nearest feature given an origin
    
    :param origin: String containing starting address we calculate
        shortest distance from
    :param feature_address_index: index where address in features
        is stored
    :param feature_type: string describing the type of feature we are
        calculating the shortest distance to
    :param error_message: string to print if we fail to find a closest feature
    :param features: list of features fetched from FeatureServer
    :return: dictionary with address, distance, and
        driving time for closest feature
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
        'features received (printing first five):',
        features[:5],            # only return first 5 features
        '...count(features):',
        len(features)
    )

    dest_addresses = _get_dest_addresses_from_features(feature_address_index, features)
    location_driving_info = g_maps_utils._get_driving_info(origin, feature_type, 
                                              dest_addresses)
    if len(location_driving_info) > 0:
        closest_location_info = min(location_driving_info,
                                    key= lambda x: x[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])
    else:
        print(error_message)
        closest_location_info = { feature_type: False,
                                  g_maps_utils.DRIVING_DISTANCE_TEXT_KEY: False,
                                  g_maps_utils.DRIVING_TIME_TEXT_KEY: False }
    closest_location_info = \
       g_maps_utils._parse_closest_location_info(feature_type, closest_location_info)
    return closest_location_info


def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)
    
    :param url: url for Feature Server
    :param query: query to select features (example: "Spaces > 0")
    :return: list of all features returned from the query
    """

    print(
        '[method: gis_utils.get_features_from_feature_server]',
        'url received:',
        url,
        'query received:',
        query
    )

    features = []
    f = FeatureLayer(url = url)
    feature_set = f.query(where = query)
    for feature in feature_set:
        features.append(feature.as_dict)
    return features


def _get_dest_addresses_from_features(feature_address_index, features):
    """
    Generate and return a list of destination addresses (as strings)
    given a list of features
    
    :param feature_address_index: to retrieve address string in feature
    :param features: list of features retrieved from FeatureServer
    :return: list of destination addresses
    """
    print(
        '[method: gis_utils._get_dest_addresses]',
        'feature_address_index received;',
        feature_address_index,
        'features received (printing first five):',
        features[:5],
        'count(features):',
        len(features)
    )
    dest_addresses = []

    # build array of each feature location
    for feature in features:
        if feature[feature_address_index]:
            dest_address = feature[feature_address_index].rstrip() # to strip \r\n 
            dest_address += " Boston, MA"
            dest_addresses.append(dest_address)
    return dest_addresses
