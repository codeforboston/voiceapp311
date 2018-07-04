"""
Utility functions using Google Maps to find driving distances/times from
an origin address to a list of destinations
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)


GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
DRIVING_DISTANCE_VALUE_KEY = "Driving distance"
DRIVING_DISTANCE_TEXT_KEY = "Driving distance text"
DRIVING_TIME_VALUE_KEY = "Driving time"
DRIVING_TIME_TEXT_KEY = "Driving time text"


def _get_driving_info(origin, location_type, destinations):
    """
    Gets the driving info from the provided origin address to each destination
    address
    
    :param origin: string containing driving starting address
    :param location_type: string that identifies type of location we're getting 
        directions to
    :param destinations: list of destination address strings (to calculate
        driving info from origin address)
    :return: list of dictionaries representing driving data for each
        destination address with address, distance, and driving time
        from origin address
    """
    logger.debug(
        'origin received: ' + str(origin) +
        ', feature_type received: ' + str(location_type) +
        ', destinations received (last five): ' + str(destinations[:5]) +
        ', count(destinations): ' + str(len(destinations))
    )

    url_parameters = _setup_google_maps_query_params(origin, destinations)
    driving_directions_url = GOOGLE_MAPS_URL
    driving_infos = None
    with requests.Session() as session:
        response = session.get(driving_directions_url, params=url_parameters)
        if response.status_code == requests.codes.ok:
            all_driving_data = response.json()
            driving_infos = combine_driving_data_with_destinations(
                all_driving_data,
                location_type,
                destinations
            )
        else:
            logger.warning("Failed to get driving directions")

    return driving_infos


def _setup_google_maps_query_params(origin, destinations):
    """
    Builds a dictionary for querying Google Maps 
    
    :param origin: "from" address in query
    :param destinations: "to" addresses in query
    :return: a dictionary to use as url parameters for query
    """
    logger.debug(
        'origin received: ' + str(origin) +
        ', destinations received (last five): ' + str(destinations[:5]) +
        ', count(destinations): ' + str(len(destinations))
    )
    return {"origins": origin,
            "destinations": '|'.join(destinations),
            "key": GOOGLE_MAPS_API_KEY,
            "units": "imperial"}


def combine_driving_data_with_destinations(
        all_driving_data,
        location_type,
        destinations
):
    """
    Retrieve data from Google Maps query into dictionary with data stored as
    key, value pairs (our keys being the constants defined at beginning
    of file) and append
    
    :param all_driving_data: JSON blob returned from Google Maps query
    :param location_type: string that identifies type of location
        we're driving to
    :param destinations: list of strings representing destination addresses
    :return: list of dictionaries representing driving data for
        each address
    """
    logger.debug(
        'all_driving_data received: ' + str(all_driving_data) +
        ', location_type received: ' + str(location_type) +
        ', destinations received (last five): ' + str(destinations[:5]) +
        ', count(destinations): ' + str(len(destinations))
    )

    driving_infos = []
    try:
        driving_data_row = all_driving_data["rows"][0]
        for (driving_data, address) in zip(
                driving_data_row["elements"],
                destinations
        ):
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
                    location_type: address}
                driving_infos.append(driving_info)
            except KeyError:
                logger.debug(
                    "Could not parse driving info {}".format(driving_data)
                )
    except KeyError:
        pass
    finally:
        return driving_infos


def parse_closest_location_info(location_type, closest_location_info):
    """
    Return a sub-dictionary of the dictionary returned by the Google Maps
    estimated driving time call
    
    :param location_type: string that describes the type of location we
        are finding the closest instance of
    :param closest_location_info: a dictionary with keys
        'Driving distance', 'Driving distance text', 'Driving time', 
        'Driving time text', feature_type.
    :return: a trimmed dictionary with keys: feature_type,
                                             DRIVING_DISTANCE_TEXT_KEY,
                                             DRIVING_TIME_TEXT_KEY
    """
    logger.debug(
        'location_type received: ' + str(location_type) +
        ', closest_location_info received: ' + str(closest_location_info)
    )
    
    keys_to_keep = [location_type, DRIVING_DISTANCE_TEXT_KEY, DRIVING_TIME_TEXT_KEY]
    return {key:closest_location_info[key] for key in keys_to_keep}




