"""
Utilities for querying with the Boston crime incidents API

"""

import logging
import typing

import requests

from mycity.utilities.common_types import ComplexDict
from mycity.utilities.gis_utils import geocode_address

RESOURCEID = "12cb3883-56f5-47de-afa5-3b1cf61b257b"
QUERY_LIMIT = 5
CRIME_INCIDENTS_SQL_URL = \
    "https://data.boston.gov/api/3/action/datastore_search_sql"

logger = logging.getLogger(__name__)


def get_crime_incident_response(address: str) -> ComplexDict:
    """
    Executes and returns the crime incident request response

    :param address: address to query
    :return: the raw json response

    """
    url_parameters = {"sql": _build_query_string(address)}
    logger.debug("Finding crime incidents information for {} using query {}".format(address, url_parameters))
    with requests.Session() as session:
        response = session.get(CRIME_INCIDENTS_SQL_URL, params=url_parameters)

    if response.status_code == requests.codes.ok:
        return response.json()
    return {}


def _build_query_string(address: str) -> str:
    """
    Builds the SQL query given an address

    :param address: address to query
    :return: a SQL query string

    """
    coordinates = _get_coordinates_for_address(address)
    return """SELECT * FROM "{}" WHERE "Lat" LIKE '{}%' AND \
        "Long" LIKE '{}%' LIMIT {}""" \
        .format(RESOURCEID,
                coordinates[0],
                coordinates[1],
                QUERY_LIMIT)


def _get_coordinates_for_address(address: str) -> typing.Tuple[str, str]:
    """
    Populates the GPS coordinates for the provided address

    :param address: address to query
    :return: a tuple of the form (lat, long)

    """
    coordinates = geocode_address(address)
    logger.debug("Got coordinates: {}".format(coordinates))
    _lat = "{:.2f}".format(float(coordinates['y']))
    _long = "{:.2f}".format(float(coordinates['x']))
    return _lat, _long
