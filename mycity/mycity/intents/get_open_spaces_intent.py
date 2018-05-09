"""
Find the closest public park or open space to user's address

"""

import csv
import requests

import mycity.intents.intent_constants as intent_constants
import mycity.mycity_response_data_model as mcrd
import mycity.utilities.address_utils as address_utils
import mycity.utilities.csv_utils as csv_utils
import mycity.utilities.google_maps_utils as g_maps_utils

OPEN_SPACES_INFO_URL = ("http://bostonopendata-boston.opendata.arcgis.com"
                        "/datasets/2868d370c55d4d458d4ae2224ef8cddd_7.csv")

def get_open_spaces_intent(request):
    """
    Populate MyCityResponseDataModel with information about the closest open
    space

    :param request: MyCityRequestModel object
    :return: MyCityResponseModel object
    """
    print('[method: get_open_spaces_intent]',
          'MyCityRequestDataModel received:',
          str(request)
          )
    response = mcrd.MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in request.session_attributes:
        origin_address = address_utils.build_origin_address(request)
        print("Finding closest open space for {}".format(origin_address))
        open_spaces = get_open_spaces()
        closest_park, distance, time = \
            get_closest_open_space(origin_address, open_spaces)
        if not closest_park:
            response.output_speech = "Uh oh. Something went wrong!"
        else:
            response.output_speech = \
                ("The closest park, {}, is at {}. It is {} away and should"
                 "take you {} to drive there.")
            response.should_end_session = False
    else:
        print("Error: Called open_spaces_intent with no address")

    response.reprompt_text = None
    response.session_attributes = request.session_attributes
    response.card_title = request.intent_name

    return response


def get_closest_open_space(origin_address, open_spaces):
    """
    Calculates the address, distance, and driviing_time for the closest
    open space

    :param: origin_address : string containing the address used to find the
    closest park
    :param: open_spaces: a list of Record namedtuples with attributes taken
    from Open Spaces CSV
    :return: the Record closest to origin_address, with driving time and 
    distance recorded as strings
    """
    print(
        '[method: get_closest_open_space]'
        'origin_address received:',
        origin_address,
        'open_spaces:',
        open_spaces
        )
    addr_to_record = csv_utils.map_addresses_to_records(open_spaces)
    destinations = [park.Address for park in open_spaces]
    all_parks = g_maps_utils._get_driving_info(origin_address,
                                               "Open Space",
                                               destinations)
    if all_parks:
        shortest_drive = min(all_parks,
                             key = lambda park: park[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])
        closest_addr = shortest_drive["Open Space"]
        return (addr_to_record[closest_addr],
                shortest_drive[g_maps_utils.DRIVING_DISTANCE_TEXT_KEY],
                shortest_drive[g_maps_utils.DRIVING_TIME_TEXT_KEY])

def get_open_spaces():
    """
    Return a list of namedtuples from the csv_reader fetched by _get_open_spaces

    :return: reader: csv_reader

    """

    print('[method: get_open_spaces]')
    reader = _get_open_spaces()
    if reader:
        return convert_csv_reader_into_namedtuples(reader)

def _get_open_spaces():
    """
    Build a csv_reader object from csv fetched at 
    OPEN_SPACES_INFO_URL

    :return: reader if request is OK. None if request fails
    """
    print('[method: _get_open_spaces]')
    print('Retrieving csv file from {}'.format(PARKING_INFO_URL))
    r = requests.get(PARKING_INFO_URL)
    if r.status_code == 200:
        file_contents = r.content.decode(r.apparent_encoding)
        reader = csv.reader(file_contents.splitlines(), delimiter = ',')
        return reader


def convert_csv_reader_into_namedtuples(reader):
    """
    Build a list of parking location records from a csv_reader.

    :return records: list of namedtuple records
    """
    print('[method: convert_csv_reader_into_namedtuples]')
    print('reader: ' + str(reader))
    model = csv_utils.create_record_model("Record", 
                                              next(reader)) # consume header
    records = csv_utils.csv_to_namedtuples(model, reader)
    records = csv_utils.add_city_and_state_to_records(records,
                                                      "Boston",
                                                      "MA")
    print("Printing first five records...")
    print(records[:5])
    return records
