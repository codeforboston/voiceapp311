import logging
import os
import typing

import requests

from mycity.utilities.common_types import ComplexDict, StrDict

logger = logging.getLogger(__name__)

DRIVING_DISTANCE_TEXT_KEY = "Driving_distance"
DRIVING_TIME_TEXT_KEY = "Driving_time"
ARCGIS_CLIENT_ID_STR = "ARCGIS_CLIENT_ID"
ARCGIS_CLIENT_SECRET_STR = "ARCGIS_CLIENT_SECRET"
EMPTY_RECORD = ""
ARCGIS_AUTH_URL = "https://www.arcgis.com/sharing/rest/oauth2/token"
ARCGIS_CLOSEST_FACILITY_URL = "https://route.arcgis.com/arcgis/rest/services/World/ClosestFacility/NAServer/ClosestFacility_World/solveClosestFacility"
ARCGIS_GEOCODE_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"


def generate_access_token() -> typing.Optional[str]:
    """
    Generates a temporary access token fro ArcGIS REST APIs

    :return: String containing temporary access token
    """
    try:
        client_id = get_client_id()
        client_secret = get_client_secret()
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {}
        response = _post_request(ARCGIS_AUTH_URL, payload, headers)
        if response.status_code == 200:
            response_json = response.json()
            access_token = response_json['access_token']
            return access_token
        else:
            logger.debug("Response Error: {}, Response: {}".format(str(response.status_code), response.text))
            return None

    except Exception as e:
        logger.debug(e)
        return None


def get_client_id() -> str:
    """
    Returns Client ID environment variable

    :return: String containing ArcGIS client ID
    """
    client_id = os.getenv(ARCGIS_CLIENT_ID_STR)
    if not client_id:
        raise Exception('ARCGIS_CLIENT_ID Environment variable not set')
    else:
        return client_id


def get_client_secret() -> str:
    """
    Returns Client Secret environment variable

    :return: String containing ArcGIS client ID
    """
    client_secret = os.getenv(ARCGIS_CLIENT_SECRET_STR)
    if not client_secret:
        raise Exception('ARCGIS_CLIENT_SECRET Environment variable not set')
    else:
        return client_secret


def find_closest_route(api_access_token: str,
                       origin_address: StrDict,
                       destination_addresses: typing.Dict[typing.Tuple[str, str], str]) -> typing.Optional[StrDict]:
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

    # (x, y) coordinates of origin address
    try:
        incidents = "{},{}".format(origin_address['x'], origin_address['y'])
    except KeyError as e:
        logger.debug("Missing coordinate in orgin_address - {}".format(str(e)))
        return None

    # List of (x, y) coordinates of possible destinations
    facility_list = []
    facility_key_list = list(
        filter(lambda k: k[0] != EMPTY_RECORD and k[1] != EMPTY_RECORD, destination_addresses.keys())
    )
    facility_list = map(lambda k: "{},{}".format(k[0], k[1]), facility_key_list)
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

    body_as_string, updated_header = format_multipart_form_request(ARCGIS_CLOSEST_FACILITY_URL, params)
    # POST request over network
    response = _post_request(ARCGIS_CLOSEST_FACILITY_URL, body_as_string, updated_header)

    if response.status_code == 200:
        response_json = response.json()
        logger.debug("Response JSON: {}".format(str(response_json)))
        try:
            routes = response_json['routes']
            features = routes['features']
            attributes = features[0]['attributes']
            facility_id = attributes['FacilityID']
            travel_time_in_minutes = attributes['Total_TravelTime']
            travel_distance_in_miles = attributes['Total_Miles']
        except KeyError as e:
            logger.debug(str(e))
            return None

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
    else:
        logger.debug("Response Error: {}".format(str(response.status_code)))
        return None


def format_multipart_form_request(url: str, params: StrDict) -> typing.Tuple[str, StrDict]:
    """
    Formats a multipart/form POST request
    for requests module properly for
    ESRI ArcGIS API

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


def _modify_multipart_form_params(params: StrDict) -> typing.Dict[str, typing.Tuple[type(None), str]]:
    """
    Helper function for _format_multipart_form_request
    that properly formats param dictionary

    :param params: Dictionary of request body paramters
    :return Dictionary of updated request body parameters
    """
    updated_params = {}
    for key, value in params.items():
        updated_params[key] = (None, str(value))
    logger.debug("Updated Parameters: {}".format(str(updated_params)))
    return updated_params


def _format_float(input_float: float) -> str:
    """
    Takes a float and returns a formatted String

    :param input_float: Floating point number
    :return: String from a floating point number,
        rounded to two decimals
    """

    rounded = round(input_float, 2)
    as_string = str(rounded)
    return as_string


def _post_request(url: str, params: typing.Union[str, StrDict], headers: StrDict) -> requests.Response:
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


def geocode_address_candidates(input_address: str) -> typing.Optional[ComplexDict]:
    """
    Finds candidate addresses from ArcGIS Geocoding service
    based on input address string

    :param input_address: String of address to be geocoded
    :return: JSON object containing geocoded address candidates
    """
    logger.debug("Input Address: {}".format(input_address))

    params = {
        "f": "json",
        "singleLine": input_address,
        "outFields": "Match_addr,Addr_type"
    }
    response = requests.request("GET", ARCGIS_GEOCODE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def select_top_address_candidate(geocode_candidate_response_json: ComplexDict) -> typing.Union[int, StrDict]:
    """
    Selects the geocoded address candidate with the highest score

    :param geocode_candidate_response_json: JSON object containing address candidates
        returned from the ArcGIS Geodcoding API
    :return: Dict containing address string and
        location information ((X, Y) coordinates)
    """

    candidates = geocode_candidate_response_json['candidates']

    if not candidates:
        return -1
    else:
        top_candidate = max(candidates, key=lambda candidate: candidate['score'])
        address_string = top_candidate['address']
        x_coordinate = top_candidate['location']['x']
        y_coordinate = top_candidate['location']['y']

        coordinate_dict = {
            'address': address_string,
            'x': x_coordinate,
            'y': y_coordinate
        }
        return coordinate_dict
