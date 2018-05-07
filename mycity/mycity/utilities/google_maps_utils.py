"""
Utility functions using Google Maps to find driving distances/times from
an origin address to a list of destinations
"""

import os
import requests



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
    :param destinations: array of address to calculate driving info from origin
    address
    :param feature_name: string representing name of this feature
    :param feature_key: string that identifies type of feature we're getting 
    directions to 
    :return driving_infos: dictionary with address, distance, and driving time from origin
    address
    """
    print(
        '[method: google_maps_utils.._get_driving_info]',
        'origin received:',
        origin,
        'feature_type received:',
        feature_type,
        'destinations received (printing first five):',
        destinations[:5],       # only print first five destinations
        'count(destinations):',
        len(destinations)
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
        '[method: google_maps_utils._setup_google_maps_query]',
        'origin received:',
        origin,
        'destinations received (printing first five):',
        destinations[:5],       # only print first five destinations
        'count(destinations):',
        len(destinations)
    )
    return {"origins": origin,
            "destinations": '|'.join(destinations),
            "key": GOOGLE_MAPS_API_KEY,
            "units": "imperial"}


def _parse_driving_data(all_driving_data, location_type, destinations):
    """
    Retrieve data from Google Maps query into dictionary with data stored as
    key, value pairs (our keys being the constants defined at beginning of file)
    and append
    
    :param all_driving_data: JSON blob returned from Google Maps query
    :param destinations: list of destination addresses
    :param location_type: string that identifies type of location we're driving to
    :return driving_infos: list of dictionaries representing driving data for
    each address
    
    """
    print(
        '[method: google_maps_utils._parse_driving_data]',
        'all_driving_data received:',
        all_driving_data,
        'location_type received:',
        location_type,
        'destinations received (printing first five):',
        destinations[:5],       # only print first five 
        'count(destinations):',
        len(destinations)
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
                    location_type: address}
                driving_infos.append(driving_info)
            except KeyError:
                print("Could not parse driving info {}".format(driving_data))
    except KeyError:
        pass
    finally:
        return driving_infos


def _parse_closest_location_info(location_type, closest_location_info):
    """
    Return a sub-dictionary of the dictionary returned by the Google Maps
    estimated driving time call
    :param: location_type: string that describes the type of location we
    are finding the closest instance of
    :param: closest_location_info: a dictionary with keys
    'Driving distance', 'Driving distance text', 'Driving time', 
    'Driving time text', feature_type.
    :return pruned: a dictionary with keys feature_type,
                                  DRIVING_DISTANCE_TEXT_KEY,
                                  DRIVING_TIME_TEXT_KEY
    """
    print(
        '[method: google_maps_utils._parse_closest_location_info]',
        'location_type received:',
        location_type,
        'closest_location_info received:',
        closest_location_info
    )
    keys_to_keep = [location_type, DRIVING_DISTANCE_TEXT_KEY, DRIVING_TIME_TEXT_KEY]
    return {key:closest_location_info[key] for key in keys_to_keep}




