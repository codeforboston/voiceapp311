"""
Utilty functions that interact with ArcGIS Feature Servers

NOTE: Intents that query FeatureServers may fail because AWS will
kill any computation that takes longer than 3 secs.

"""

from arcgis.gis import *
from arcgis.features import FeatureLayer
from arcgis.geocoding import geocode
from math import sin, cos, sqrt, atan2, radians
import logging

logger = logging.getLogger(__name__)

dev_gis = GIS()  # this is needed to use geocoding


def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)
    
    :param url: url for Feature Server
    :param query: query to select features (example: "Spaces > 0")
    :return: list of all features returned from the query
    """

    logger.debug('url received: ' + url + ', query received: ' + query)

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
    logger.debug(
        'feature_address_index received; ' + str(feature_address_index) +
        ', features received (printing first five): ' + str(features[:5]) +
        ', count(features): ' + str(len(features))
    )
    
    dest_addresses = []

    # build array of each feature location
    for feature in features:
        if feature[feature_address_index]:
            dest_address = feature[feature_address_index].rstrip() # to strip \r\n 
            dest_address += " Boston, MA"
            dest_addresses.append(dest_address)
    return dest_addresses


def geocode_address(m_address):
    """
    :param m_address: address of interest in street form
    :return: address in coordinate (X and Y) form
    """
    m_address = m_address + ", City: Boston, State: MA"
    m_location = geocode(address=m_address)[0]
    adict = (m_location['location'])
    return list(adict.values())


def calculate_distance(m_first, m_second):
    """
    :param m_first: first address of interest
    :param m_second: second address of interest
    :return: the distance (in km) between these two addresses using the Haversine formula
    """
    R = 6371  # radius of the earth
    lat1 = radians(m_first[0])
    lon1 = radians(m_first[1])
    lat2 = radians(m_second[0])
    lon2 = radians(m_second[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
