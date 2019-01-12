"""
Functions for Alexa responses related to food trucks.
The data comes back from the ARCGIS server in the following format:

{'geometry':
    {'x': -7910683.074890779, 'y': 5214470.286921388},
'attributes':
    {'FID': 396,
    'Time': 'Lunch',
    'Day': 'Wednesday',
    'Truck': 'Cookie Monstah',
    'Loc': 'Brewer Fountain Plaza (near Park Street Station)',
    'Hours': '11 a.m. - 3 p.m.',
    'Title': 'Boston Common',
    'Site_num': 0,
    'Management': 'Friends of the Public Garden',
    'Notes': None,
    'POINT_X': -7910683.075,
    'POINT_Y': 5214470.287,
    'Link': 'http://www.thecookiemonstah.com/',
    'Start_time': '3:00:00 PM',
    'End_time': '7:00:00 PM',
    'GlobalID': '4148e021-6153-45d9-9af3-0754b15746db',
    'CreationDate': 1523998053973,
    'Creator': '143525_boston',
    'EditDate': 1523998053973,
    'Editor': '143525_boston'
    }
}

We filter the data in `get_truck_locations()` and put it on a list.

"""
import mycity.utilities.gis_utils as gis_utils
from mycity.intents.intent_constants import CURRENT_ADDRESS_KEY
from mycity.mycity_response_data_model import MyCityResponseDataModel
from streetaddress import StreetAddressParser
from datetime import date
from calendar import day_name
import logging
from pyproj import Proj, transform
from .custom_errors import \
    InvalidAddressError, BadAPIResponse

logger = logging.getLogger(__name__)

'''
The variables below define a pseudo-mercator coordination system,
i.e., it uses X,Y instead of lat,long (ref.: https://epsg.io/3857)
and the geodetic coordinate system i.e., lat, long. (ref.: https://epsg.io/4326)
'''
MERCATOR = 'epsg:3857'
GEODETIC = 'epsg:4326'
MILE_IN_KILOMETERS = 1.6


def convert_xy_to_lat_long(coordinates):
    """
    Some datasets use (x,y) coordinates to form map projection.
    This method converts it to lat and long
    :param coordinates: a list with X and Y
    :return: a list of Lat and Long
    """
    inProj = Proj(init=MERCATOR)
    outProj = Proj(init=GEODETIC)
    return [coordinate for coordinate
            in transform(inProj, outProj, coordinates[0], coordinates[1])]


def get_truck_locations():
    """
    Queries arcgis data and returns a list of food truck locations in Boston

    :return: list of lists containing location name, dict ofGPS coordinates
    in value for example:
    [['Sumner Street', {'x': -7908107.9125, 'y': 5216395.7579}],
    ['Boylston/Clarendon by Trinity Church', {'x': -7912059.823100001,
    'y': 5213652.076399997}]]
    """
    food_truck_feature_server_url = \
        'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/' \
        + 'food_trucks_schedule/FeatureServer/0'
    day_of_week = day_name[date.today().weekday()]

    # Note: as currently written, only fetch Lunch food trucks on that day
    food_truck_query = 'Day=\'%(day)s\' AND Time=\'%(meal)s\'' \
                       % {'day': day_of_week, "meal": "Lunch"}

    # Result is a dictionary of food truck locations
    food_truck_data_result = \
        gis_utils.get_features_from_feature_server(
            food_truck_feature_server_url, food_truck_query)

    # Generate unique list of food truck locations
    # to send to the Google Maps API
    truck_unique_locations = []
    for truck in food_truck_data_result:
        if truck["attributes"]["Loc"] not in truck_unique_locations:
            truck_unique_locations.append([truck["geometry"],
                                           truck["attributes"]["Truck"],
                                           truck["attributes"]["Loc"],
                                           truck["attributes"]["Title"],
                                           truck["attributes"]["Start_time"],
                                           truck["attributes"]["End_time"]])

    return truck_unique_locations


def get_nearby_food_trucks(mycity_request):
    """
    Gets food truck info near an address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    mycity_response = MyCityResponseDataModel()

    # Get current address location
    if CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = \
            mycity_request.session_attributes[CURRENT_ADDRESS_KEY]

        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        address = str(a['house']) + " " + str(a['street_name']) + " " \
                  + str(a['street_type'])

        # Convert address to X, Y
        usr_addr_xy = gis_utils.geocode_address(address)
        truck_unique_locations = get_truck_locations()

        nearby_food_trucks = []
        try:
            for location in truck_unique_locations:
                permit_xy = list(location[0].values())
                permit_xy = convert_xy_to_lat_long(permit_xy)
                dist = gis_utils.calculate_distance(usr_addr_xy, permit_xy)

                if dist <= MILE_IN_KILOMETERS:
                    nearby_food_trucks.append(location)
                else:
                    continue

            count = len(nearby_food_trucks)
            print(count)
            if count == 1:
                mycity_response.output_speech = \
                    f"I found {count} food truck within a mile from " \
                    f"your address.! {nearby_food_trucks[0][1]} is " \
                    f"located at {nearby_food_trucks[0][2]} and " \
                    f"{nearby_food_trucks[0][3]}, from " \
                    f"{nearby_food_trucks[0][4]} to " \
                    f"{nearby_food_trucks[0][5]}"
            elif count == 2:
                response = f"I found {count} food trucks within a mile " \
                    "from your address! "

                for i in range(count):
                    print(response)
                    response += f"{nearby_food_trucks[i][1]} is located at " \
                        f"{nearby_food_trucks[i][2]} and " \
                        f"{nearby_food_trucks[i][3]}, from " \
                        f"{nearby_food_trucks[i][4]} to " \
                        f"{nearby_food_trucks[i][5]}, "
                print(response)
                mycity_response.output_speech = response

            elif count > 2:
                response = f"I found {count} food trucks within a mile " \
                    "from your address! Here are the first three: "
                for i in range(3):
                    response += f"{nearby_food_trucks[i][1]} is located at "\
                        f"{nearby_food_trucks[i][2]} and " \
                        f"{nearby_food_trucks[i][3]}, from " \
                        f"{nearby_food_trucks[i][4]} to " \
                        f"{nearby_food_trucks[i][5]}, "
                response += "Would you like to hear more?"
                print(response)
                mycity_response.output_speech = response
            else:
                mycity_response.output_speech = "I didn't find any trucks!"

        except InvalidAddressError:
            address_string = address

            mycity_response.output_speech = \
                "I can't seem to find {address_string}. Try another address"
            mycity_response.reprompt_text = None
            mycity_response.session_attributes = \
                mycity_request.session_attributes
            mycity_response.card_title = "Food Trucks"
            mycity_request = clear_address_from_mycity_object(mycity_request)
            mycity_response = clear_address_from_mycity_object(mycity_response)
            return mycity_response

        except BadAPIResponse:
            mycity_response.output_speech = \
                "Hmm something went wrong. Maybe try again?"

    else:
        logger.error("Error: Called food_truck_intent with no address")
        mycity_response.output_speech = "I didn't understand that address, " \
                                        "please try again"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Food Trucks"

    return mycity_response
