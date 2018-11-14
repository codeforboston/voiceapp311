import requests
import json
import os
import sys
import urllib
import logging

logger = logging.getLogger(__name__)

DRIVING_DISTANCE_TEXT_KEY = "Driving_distance"
DRIVING_TIME_TEXT_KEY = "Driving_time"

def generate_access_token():
    """
    Generates a temporary access token fro ArcGIS REST APIs

    :return: String containing temporary access token
    """

    try:
        client_id = os.getenv('ARCGIS_CLIENT_ID')
    except:
        logger.debug("ARCGIS_CLIENT_ID environment variable not set")
        return None

    try:
        client_secret = os.getenv('ARCGIS_CLIENT_SECRET')
    except:
        logger.debug("ARCGIS_CLIENT_SECRET environment variable not set")
        return None

    payload = {
        'client_id': client_id,
        'client_secret' : client_secret, 
        'grant_type' : 'client_credentials'
        }

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json",
        'cache-control': "no-cache"
        }

    base_url = "https://www.arcgis.com/sharing/rest/oauth2/token"
    response = _post_request(base_url, payload, headers)
    if response.status_code != 200:
        logger.debug("Response Error: {}, Response: {}".format(str(response.status_code), response.text))
        return None
    else:
        response_json = response.json()
        access_token = response_json['access_token']
        return access_token
    



def find_closest_route(api_access_token, origin_address, destination_addresses):
    """
    Finds the closest route, by driving distance,
    given the coordinates of an origin and possible destinations

    :param api_access_token: String containing temporary ArcGIS REST API access token
    :param origin_address: Dictionary containing coordinates and address string of origin
    :param destination_addresses: Dictionary with (x, y) coordinate values as the keys,
        and the associated address string as the values
    :return: Dictionary containing address, driving time and driving distance of closest destination
    """
    logger.debug("api_access_token: {} ".format(api_access_token) \
                + "origin_address: {} ".format(str(origin_address)) \
                + "destination_addresses: {}".format(str(destination_addresses))
            )

    base_url = "https://route.arcgis.com/arcgis/rest/services/World/ClosestFacility/NAServer/ClosestFacility_World/solveClosestFacility"
    
    # (x, y) coordinates of origin address
    incidents = "{},{}".format(origin_address['x'], origin_address['y'])

    # List of (x, y) coordinates of possible destinations
    facility_list = []
    facility_key_list = []
    for k in destination_addresses.keys():
        if k[0] != "" and k[1] != "":
            temp_str = "{},{}".format(k[0], k[1])
            facility_list.append(temp_str)
            facility_key_list.append(k)
    
    # Separate destination coordinates with ";"
    facilities = ";".join(facility_list)
    params = {
            'f': 'json',
            'token': api_access_token,
            'returnDirections': 'false',
            'returnCFRoutes': 'true',
            'incidents': incidents,
            'facilities': facilities
            }

    formatted_tuple = format_multipart_form_request(base_url, params)
    body_as_string = formatted_tuple[0]
    updated_header = formatted_tuple[1]
    # POST request over network
    response = _post_request(base_url, body_as_string, updated_header)

    if response.status_code != 200:
        logger.debug("Response Error: {}".format(str(response.status_code)))
        return None
    else:
        response_json = response.json()
        logger.debug("Response JSON: {}".format(str(response_json)))

        routes = response_json['routes']
        features = routes['features']
        attributes = features[0]['attributes']
        facility_id = attributes['FacilityID']
        travel_time_in_minutes = attributes['Total_TravelTime']
        travel_distance_in_miles = attributes['Total_Miles']

        formatted_travel_time_in_minutes = _format_float(float(travel_time_in_minutes))
        formatted_travel_distance_in_miles = _format_float(float(travel_distance_in_miles))

        travel_time_string = "{} minutes".format(formatted_travel_time_in_minutes)
        travel_distance_string = "{} miles".format(formatted_travel_distance_in_miles)

        facility_key_index = int(facility_id) - 1
        facility_key = facility_key_list[facility_key_index]
        facility_address = destination_addresses[facility_key]

        destination_dict = {
                'Address': facility_address,
                'Driving_time': travel_time_string,
                'Driving_distance': travel_distance_string
                }

        logger.debug("Returning closest destination: {}".format(str(destination_dict)))
        return destination_dict


def format_multipart_form_request(url, params):
    """
    Formats a multipart/form POST request
    for requests module properly for
    ESRI ARCGis API

    :param url: String containg URL of API
    :param params: Dictionary of paramters
    :return Two-Tuple containing 1) String representing
        params to be passed as data to POST request
        and 2) Dictionary with modified headers
    """
    logger.debug("URL: {}, Params: {}".format(url, str(params)))

    updated_params = _modify_multipart_form_params(params)
    req = requests.Request('POST', url, files=updated_params)
    prepared_request = req.prepare()

    updated_header = prepared_request.headers
    updated_header.pop('Content-Length')
    updated_header['cache-control'] = "no-cache"

    # Change body from byte string to string
    body_as_bytes = prepared_request.body
    body_as_string = body_as_bytes.decode('utf-8')

    return (body_as_string, updated_header)




def _modify_multipart_form_params(params):
    """
    Helper function for _format_multipart_form_request
    that properly formats param dictionary

    :param params: Dictionary of request body paramters
    :return Dictionary of updated request body parameters
    """
    updated_params = {}
    for key in params:
        value = params[key]
        updated_params[key] = (None, str(value))
    logger.debug("Updated Parameters: {}".format(str(updated_params)))
    return updated_params




def _format_float(input_float):
    """
    Takes a float and returns a formatted String

    :param input_float: Floating point number
    :return: String from a floating point number,
        rounded to two decimals
    """

    rounded = round(input_float, 2)
    as_string = str(rounded)
    return as_string

def _post_request(url, params, headers):
    """
    Utilizes requests module to formulate
    HTTP POST request over the network

    :param url: String representing base URL of request
    :param params: String or Dictionary containing parameters
    :param headers: Dictionary containing headers
    :return: request.Response object
    """
    logger.debug("URL: {}, Params: {}, Headers: {}".format(url, str(params), str(headers)))

    session = requests.Session()
    request = requests.Request("POST", url, data=params, headers=headers)
    prepared_request = request.prepare()
    response = session.send(prepared_request)
    return response



def geocode_address_candidates(input_address):
    """
    Finds candidate addresses from ArcGIS Geocoding service
    based on input address string

    :param input_address: String of address to be geocoded
    :return: JSON object containing geocoded address candidates
    """
    logger.debug("Input Address: {}".format(input_address))

    base_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    params = {
            "f": "json",
            "singleLine": input_address,
            "outFields":"Match_addr,Addr_type"
            }
    headers = {
            'cache-control': "no-cache"
            }

    response = requests.request("GET", base_url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    else:
        return response.json()


def select_top_address_candidate(geocode_candidate_response_json):
    """
    Selects the geocoded address candidate with the highest score

    :param geocode_candidate_response_json: JSON object containing address candidates
        returned from the ArcGIS Geodcoding API
    :return: Dict containing address string and
        location information ((X, Y) coordinates)
    """

    candidates = geocode_candidate_response_json['candidates']
    logger.debug("Geocode Candidates: " + str(candidates))

    if len(candidates) == 0:
        return None
    else:
        top_score = -1.0
        top_candidate = None
        for candidate in candidates:
            if candidate['score'] > top_score:
                top_candidate = candidate
                top_score = candidate['score']

        address_string = top_candidate['address']
        x_coordinate = top_candidate['location']['x']
        y_coordinate = top_candidate['location']['y']

        logger.debug("Top Candidate: {} ".format(address_string) \
                + "Candidate Score: {}".format(str(top_score)))

        coordinate_dict = {
                'address': address_string,
                'x': x_coordinate,
                'y': y_coordinate
                }
        return coordinate_dict

def get_ward_precinct_info(coordinates):
    
    base_url = "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/Precincts_2017/FeatureServer/0/query"

    params = {
        "f": "json",
        "geometry": coordinates['x'] + "," + coordinates['y'],
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "returnGeometry": "false",
        "outFields": "WARD_PRECINCT"
    }

    response = requests.request("GET", base_url, params=params)
    if response.status_code != 200:
        return "None"
    else:
        res_data = json.loads(response.text)
        print(res_data)
        return res_data['features'][0]['attributes']['WARD_PRECINCT']

