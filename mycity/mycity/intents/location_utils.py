""" 
Utility functions for building addresses and finding the closest feature to an
address.

Common code used across intents to build a string using the MyCity object to
represent the user's address


"""

from . import intent_constants
from arcgis.features import FeatureLayer
from streetaddress import StreetAddressParser


def build_origin_address(mcd):
    """
    Builds an address from an Alexa session. Assumes city is Boston if not
    specified

    :param mcd: MyCityDataModel object
    :return: String containing full address
    """
    print(
        '[method: _build_origin_address]',
        'MyCityDataModel received:',
        str(mcd)
    )

    address_parser = StreetAddressParser()
    current_address = \
        mcd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY]
    parsed_address = address_parser.parse(current_address)
    origin_address = " ".join([parsed_address["house"],
                               parsed_address["street_full"]])
    if parsed_address["other"]:
        origin_address += " {}".format(parsed_address["other"])
    else:
        origin_address += " Boston MA"

    return origin_address



def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)

    :param url: url for Feature Server
    :param query: query to select features (example: "Spaces > 0")
    :return features: list of all features
    """
    features = []
    f = FeatureLayer(url = url)
    feature_set = f.query(where = query)
    for feature in feature_set:
        features.append(feature.as_row[0]) # [0] = data, [1] = column names
    return features
