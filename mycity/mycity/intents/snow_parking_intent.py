"""Alexa intent used to find snow emergency parking"""

import csv
import requests

import mycity.intents.intent_constants as intent_constants
import mycity.utilities.address_utils as address_utils
import mycity.utilities.csv_utils as csv_utils
import mycity.utilities.google_maps_utils as g_maps_utils
from mycity.mycity_response_data_model import MyCityResponseDataModel





# Constants 
PARKING_INFO_URL = ("http://bostonopendata-boston.opendata.arcgis.com/datasets/"
                    "53ebc23fcc654111b642f70e61c63852_0.csv")

def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response information.

    :param mycity_request: MyCityRequestModel object
    :param mycity_response: MyCityResponseModel object
    :return: MyCityResponseModel object
    """
    print(
        '[method: get_snow_emergency_parking_intent]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        origin_address = address_utils.build_origin_address(mycity_request) 
        print("Finding snow emergency parking for {}".format(origin_address))
        parking_locations = get_parking_locations()
        closest_location, distance, time = \
            get_closest_parking_location(origin_address, parking_locations)
        if not closest_location:
            mycity_response.output_speech = "Uh oh. Something went wrong!"
        else:
            phone_number = \
                "Call {} for information ".format(closest_location.Phone) \
                if closest_location.Phone.strip() != "" else ""
            fee = "There is a fee of {}".format(closest_location.Fee) \
                if closest_location.Fee != "No Charge" else "There is no fee. "
            comment = " NOTE: {} ".format(closest_location.Comments) \
                if closest_location.Comments.strip() != "" else ""
            mycity_response.output_speech = \
                ("The closest snow emergency parking location, {}, is at "
                "{}. It is {} away and should take you {} to drive " 
                "there. The parking lot has {} spaces when empty. {}"
                 "{} {}").format(closest_location.Name, closest_location.Address,
                               distance, time, closest_location.Spaces,
                                 fee, comment, phone_number)
            mycity_response.should_end_session = False
    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name
    
    return mycity_response




def get_closest_parking_location(origin_address, parking_locations):
    """
    Calculates the address, distance, and driving time for the closest snow
    emergency parking location.

    :param origin_address: string containing the address used to find the
    closest emergency parking location
    :param parking_locations: a list of Record namedtuples with attributes
    taken from Snow Parking CSV
    :return: the Record closest to origin_address
    """
    print(
        '[method: get_closest_parking_location]',
        'origin_address received:',
        origin_address,
        'parking_locations (first five):',
        parking_locations[:5]
    )
    addr_to_record = csv_utils.map_addresses_to_records(parking_locations)
    destinations = [location.Address for location in parking_locations] 
    all_parking_lots = g_maps_utils._get_driving_info(origin_address, 
                                                         "Parking Lot",
                                                         destinations)

    if all_parking_lots:     # if this exists, for the entry with the least
                             # driving time use the address keyed at "Parking
                             # Lot" to return the relevant record with the
                             # DRIVING_DISTANCE_TEXT_KEY and
                             # DRIVING_TIME_TEXT_KEY
        shortest_drive = min(all_parking_lots,
                             key=lambda x: x[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])
        closest_addr = shortest_drive["Parking Lot"]
        return (addr_to_record[closest_addr], 
                shortest_drive[g_maps_utils.DRIVING_DISTANCE_TEXT_KEY],
                shortest_drive[g_maps_utils.DRIVING_TIME_TEXT_KEY])


def get_parking_locations():
    print('[method: get_parking_locations]')
    reader = _get_parking_locations()
    if reader:
        return convert_csv_reader_into_namedtuples(reader)



# moving request into private function to make it more testable
def _get_parking_locations():
    """
    Build a list of parking location records from csv_file retrieved from 
    PARKING_INFO_URL

    :return None if request fails or a csv_reader object
    """
    print('[method: _get_parking_locations]')
    print('Retrieving csv file from PARKING_INFO_URL')
    r = requests.get(PARKING_INFO_URL)
    if r.status_code == 200:
        file_contents = r.content.decode(r.apparent_encoding)
        reader = csv.reader(file_contents.splitlines(), delimiter=',')
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
