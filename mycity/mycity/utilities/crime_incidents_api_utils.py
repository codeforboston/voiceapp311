"""
Utilities for querying with the Boston crime incidents API

"""

import requests
import typing
import logging
from mycity.utilities.gis_utils import geocode_address


RESOURCE_ID = "12cb3883-56f5-47de-afa5-3b1cf61b257b"
QUERY_LIMIT = 5
CRIME_INCIDENTS_SQL_URL = \
    "https://data.boston.gov/api/3/action/datastore_search_sql"
LONG_INDEX = 0
LAT_INDEX = 1

logger = logging.getLogger(__name__)


def get_crime_incident_response(address: str, _requests: typing.ClassVar = requests):
    """
    Executes and returns the crime incident request response

    :param address:  address to query
    :param _requests: Injectable request class
    :return: the raw json response

    """
    url_parameters = {"sql": _build_query_string(address)}
    logger.debug("Finding crime incidents information for {} using query {}".format(address, url_parameters))

    with _requests.Session() as session:
        response = session.get(CRIME_INCIDENTS_SQL_URL, params=url_parameters)

    if response.status_code == _requests.codes.ok:
        return response.json()
    return {}


def _get_coordinates_for_address(
        address: str,
        _geocode_address: typing.Callable[[str], list] = geocode_address)-> tuple:
    """
    Populates the GPS coordinates for the provided address

    :param address:          address to query
    :param _geocode_address: injectable function for test
    :return: a tuple of the form (lat, long)

    """
    coordinates = _geocode_address(address)
    logger.debug("Got coordinates: {}".format(coordinates))
    _lat = "{:.2f}".format(float(coordinates[LAT_INDEX]))
    _long = "{:.2f}".format(float(coordinates[LONG_INDEX]))
    return _lat, _long


def _build_query_string(
        address: str,
        _get_coordinates_for_address: typing.Callable[[str], list] = _get_coordinates_for_address)-> str:
    """
    Builds the SQL query given an address

    :param address:                      address to query
    :param _get_coordinates_for_address: injectable function for test
    :return: a SQL query string

    """
    coordinates = _get_coordinates_for_address(address)
    return """SELECT * FROM "{}" WHERE "lat" LIKE '{}%' AND \
        "long" LIKE '{}%' LIMIT {}""" \
        .format(RESOURCE_ID, coordinates[0], coordinates[1], QUERY_LIMIT)
