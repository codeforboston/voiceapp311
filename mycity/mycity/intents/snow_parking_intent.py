"""Alexa intent used to find snow emergency parking"""

from . import intent_constants
import csv
import os
import requests
from streetaddress import StreetAddressParser


GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']

DRIVING_DISTANCE_VALUE_KEY = "Driving distance"
DRIVING_DISTANCE_TEXT_KEY = "Driving distance text"
DRIVING_TIME_VALUE_KEY = "Driving time"
DRIVING_TIME_TEXT_KEY = "Driving time text"
PARKING_LOCATION_KEY = "Parking Address"

BOSTON_DATA_PARKING_ADDRESS_INDEX = 9


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

        origin_address = _build_origin_address(mcd)

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


def _build_origin_address(mcd):
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
    # @todo: Repeated code -- look into using same code here and in trash intent
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

    :return: array of emergency parking info as provided in the Boston data
    csv file
    """
    print(
        '[method: _get_emergency_parking_data]'
    )

    parking_data = []
    with requests.Session() as session:
        url = "http://bostonopendata-boston.opendata.arcgis.com/" + \
              "datasets/53ebc23fcc654111b642f70e61c63852_0.csv"
        response = session.get(url)

        if response.status_code == requests.codes.ok:
            response_data = response.content.decode()
            csv_reader = csv.reader(response_data.splitlines())
            parking_data = list(csv_reader)
        else:
            print("Failed to get parking data from Boston Open Data")

    return parking_data[1:]
