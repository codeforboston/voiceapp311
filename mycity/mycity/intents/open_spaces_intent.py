"""
Intent for finding the nearest open space (playground, ball field, etc.) to a
given address

"""

from . import intent_constants
from arcgis.features import Feature, FeatureLayer, FeatureSet




def get_open_spaces():

    """
    Retrieve open spaces from the City's webserver
    """
    open_spaces_url = "http://gis.cityofboston.gov/arcgis/rest/" \
        + "services/EnvironmentEnergy/OpenData/MapServer/7"
    f = FeatureLayer(url = open_spaces_url)
    return f
