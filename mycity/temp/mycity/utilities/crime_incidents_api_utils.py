"""
Utilities for querying with the Boston crime incidents API

"""

import requests
from mycity.utilities.gis_utils import geocode_address
import logging

RESOURCEID = "12cb3883-56f5-47de-afa5-3b1cf61b257b"
QUERY_LIMIT = 5
CRIME_INCIDENTS_SQL_URL = \
    "https://data.boston.gov/api/3/action/datastore_search_sql"

logger = logging.getLogger(__name__)


def get_crime_incident_response(origin_coordinates):
    """
    Executes and returns the crime incident request response

    :param origin_coordinates: dictionary of origin_coordinates to query.
        Expects keys of 'x' and 'y'
    :return: the raw json response

    """
    url_parameters = {"sql": _build_query_string(origin_coordinates)}
    logger.debug("Finding crime incidents information for {}, {} using query {}"
        .format(origin_coordinates['x'], origin_coordinates['y'], url_parameters))
    with requests.Session() as session:
        response = session.get(CRIME_INCIDENTS_SQL_URL, params=url_parameters)

    if response.status_code == requests.codes.ok:
        return response.json()
    return {}


def _build_query_string(origin_coordinates):
    """
    Builds the SQL query given an address

    :param address: origin_coordinates to query
    :return: a SQL query string

    """
    _lat = "{:.2f}".format(float(origin_coordinates['y']))
    _long = "{:.2f}".format(float(origin_coordinates['x']))
    return """SELECT * FROM "{}" WHERE "Lat" LIKE '{}%' AND \
        "Long" LIKE '{}%' LIMIT {}""" \
        .format(RESOURCEID,
                _lat,
                _long,
                QUERY_LIMIT)
