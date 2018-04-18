"""Alexa intent used to find snow emergency parking"""

from . import intent_constants
from location_utils import build_origin_address, get_features_from_feature_server
import csv
import os
import requests



GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']

DRIVING_DISTANCE_VALUE_KEY = "Driving distance"
DRIVING_DISTANCE_TEXT_KEY = "Driving distance text"
DRIVING_TIME_VALUE_KEY = "Driving time"
DRIVING_TIME_TEXT_KEY = "Driving time text"
PARKING_LOCATION_KEY = "Parking Address"

BOSTON_DATA_PARKING_ADDRESS_INDEX = 7 # Features store parking lot address at index


def get_snow_emergency_parking_intent(mcd):
    """
    Populate MyCityDataModel with snow emergency parking response information.

    :param mcd:
    :return:
    """
    print(
        '[method: get_snow_emergency_parking_intent]',
        'MyCityDataModel received:',
        str(mcd)
    )

    if intent_constants.CURRENT_ADDRESS_KEY in mcd.session_attributes:

        origin_address = build_origin_address(mcd)

        print("Finding snow emergency parking for {}".format(origin_address))

        parking_address, driving_distance, driving_time = \
            _get_snow_emergency_parking_location(origin_address)

        if not parking_address:
            mcd.output_speech = "Uh oh. Something went wrong!"
        else:
            mcd.output_speech = \
                "The closest snow emergency parking location is at " \
                "{}. It is {} away and should take you {} to drive " \
                "there".format(parking_address, driving_distance, driving_time)

        mcd.should_end_session = False
    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mcd.reprompt_text = None
    return mcd



def _get_snow_emergency_parking_location(origin_address):
    """
    Calculates the address, distance, and driving time for the closest snow
    emergency parking location.

    :param origin_address: string containing the address used to find the
    closest emergency parking location
    :return: parking address, distance, and driving time
    """
    print(
        '[method: _get_snow_emergency_parking_location]',
        'origin_address received:',
        origin_address
    )

    parking_data = _get_emergency_parking_data()
    closest_parking_info = _get_closest_emergency_parking(origin_address,
                                                          parking_data)
    return closest_parking_info[PARKING_LOCATION_KEY],\
        closest_parking_info[DRIVING_DISTANCE_TEXT_KEY],\
        closest_parking_info[DRIVING_TIME_TEXT_KEY]


def _get_closest_emergency_parking(origin, parking_data):
    """
    Calculates the closest emergency parking location

    :param origin: String containing starting address for closest location
    search
    :param parking_data: array of parking info provided by Boston data
    emergency parking csv file
    :return: dictionary with address, distance, and driving time for the
    closest emergency parking location
    """
    print(
        '[method: _get_closest_emergency_parking]',
        'origin received:',
        origin,
        'parking_data received:',
        parking_data
    )

    parking_addresses = []

    # Build up an array of each parking location
    for location in parking_data:
        destination_address = location[BOSTON_DATA_PARKING_ADDRESS_INDEX]
        destination_address += " Boston, MA"
        parking_addresses.append(destination_address)

    parking_location_driving_info = _get_driving_info(origin,
                                                      parking_addresses)
    if len(parking_location_driving_info) > 0:
        closest_parking_info = min(parking_location_driving_info,
                                   key=lambda x: x[DRIVING_DISTANCE_VALUE_KEY])
    else:
        print("Didn't find any parking locations")
        return {
            PARKING_LOCATION_KEY: False,
            DRIVING_DISTANCE_TEXT_KEY: False,
            DRIVING_TIME_TEXT_KEY: False
        }

    return closest_parking_info


def _get_driving_info(origin, destinations):
    """
    Gets the driving info from the provided origin address to each destination
    address

    :param origin: string containing driving starting address
    :param destinations: array of address to calculate driving info from origin
    address
    :return: dictionary with address, distance, and driving time from origin
    address
    """
    print(
        '[method: _get_driving_info]',
        'origin received:',
        origin,
        'destinations received:',
        destinations
    )

    url_parameters = {"origins": origin,
                      "destinations": '|'.join(destinations),
                      "key": GOOGLE_MAPS_API_KEY,
                      "units": "imperial"}
    driving_directions_url = "https://maps.googleapis.com/maps/api/" \
                             "distancematrix/json"

    driving_infos = []

    with requests.Session() as session:
        response = session.get(driving_directions_url, params=url_parameters)

        if response.status_code == requests.codes.ok:
            all_driving_data = response.json()
            try:
                driving_data_row = all_driving_data["rows"][0]
                for (driving_data, address) in \
                        zip(driving_data_row["elements"], destinations):
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
                            PARKING_LOCATION_KEY: address}
                        driving_infos.append(driving_info)
                    except KeyError:
                        print("Could not parse driving info {}"
                              .format(driving_data))
            except KeyError:
                return driving_infos
        else:
            print("Failed to get driving directions")

    return driving_infos


def _get_emergency_parking_data():
    """
    Gets the emergency parking info from Boston Data

    :return: array of emergency parking info as provided from City's ArcGIS
    Feature Server for snow parking lots
    """
    print(
        '[method: _get_emergency_parking_data]'
    )

    parking_url = \
        'https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services'\
        + '/SnowParking/FeatureServer/0'
    query = "Space > 0"
    return get_features_feature_server(url, query)
