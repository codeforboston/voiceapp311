"""
Utility functions that interact with ArcGIS Feature Servers

NOTE: Intents that query FeatureServers may fail because AWS will
kill any computation that takes longer than 3 secs.

"""
from arcgis.gis import *
from arcgis.features import FeatureLayer
from arcgis.geocoding import geocode
from arcgis import geometry
import logging

logger = logging.getLogger(__name__)
dev_gis = GIS()


def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)
    
    :param url: url for Feature Server
    :param query: a JSON object (example: { 'where': '1=1', 'out_sr': '4326' })
    :return: list of all features returned from the query
    """

    logger.debug('url received: ' + url + ', query received: ' + str(query))

    features = []
    f = FeatureLayer(url=url)
    feature_set = f.query(**query)
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
            dest_address = feature[feature_address_index].rstrip()
            dest_address += " Boston, MA"
            dest_addresses.append(dest_address)
    return dest_addresses


def geocode_address(m_address):
    """
    :param m_address: address of interest in street form
    :return: address in coordinate (X and Y) form
    """
    m_address = m_address + ", City: Boston, State: MA"
    if geocode(address=m_address)[0]['attributes']['Score'] > 90:
        m_location = geocode(address=m_address)[0]
    else:
        m_location = ''
    return m_location['location']


def calculate_distance(feature1, feature2):
    """
    :param feature1: the first feature
    :param feature2: the second feature
    :return: the distance (in meters) between these two addresses
    """
    geometry1 = feature1  # feature1 is the address, which is already a geometry
    geometry2 = feature2['geometry']
    spation_ref = {"wkid": 4326}
    return geometry.distance(spation_ref,
                             geometry1,
                             geometry2,
                             distance_unit='',
                             geodesic=True)['distance']
