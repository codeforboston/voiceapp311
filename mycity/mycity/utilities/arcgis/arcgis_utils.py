import requests
import json
import os
import sys
import urllib
from arcgis.
import logging

logger = logging.getLogger(__name__)


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
    'cache-control': "no-cache",
    'postman-token': "11df29d1-17d3-c58c-565f-2ca4092ddf5f"
    }

    base_url = "https://www.arcgis.com/sharing/rest/oauth2/token"
    response = requests.post(base_url, data=payload, headers=headers)
    if response.status_code != 200:
        logger.debug("Response Error: {}, Response: {}".format(str(response.status_code), response.text))
        return None
    else:
        response_json = response.json()
        access_token = response_json['access_token']
        return access_token
    


def generate_route():
    route_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
    access_token = generate_access_token() 
    stops = {
  "type":"features",
  "features":  [
      {
      "geometry": {
        "x": -118.243529,
        "y": 34.053879,
        "spatialReference": {
          "wkid": "4326"
        }
      },
      "attributes": {
        "Name": "Los Angeles City Hall"
      }
    },
    {
      "geometry": {
        "x": -118.273939,
        "y": 34.123480,
        "spatialReference": {
          "wkid": "4326"
        }
      },
      "attributes": {
        "Name": "Griffith Park"
      }
    }
  ]
}

    payload = {
        'f': 'json',
        'token': access_token,
        'stops' : json.dumps(stops)
        }


    req = requests.Request('POST',route_url, data=payload)
    prepared = req.prepare()

    s = requests.Session()
    response = s.send(prepared)

    print(response.status_code)
    print(response.json())



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
    logger.debug("api_access_token: {}\n".format(api_access_token) \
                + "origin_address: {}\n".format(str(origin_address)) \
                + "destination_addresses: {}".format(str(destination_addresses))
            )

    base_url = "https://route.arcgis.com/arcgis/rest/services/World/ClosestFacility/NAServer/ClosestFacility_World/solveClosestFacility"

    incidents = {
            "features": [
                {
                    "geometry": {
                        "x": origin_address["x"],
                        "y": origin_address["y"],
                        "spatialReference": {
                            "wkid": "4326"
                            }
                        },
                    "attributes": {
                        "Name": origin_address["address"]
                        }
                    }
                ]
            }

    print("INCIDENTS")
    print(incidents)

    features = []
    for k in destination_addresses.keys():
        temp_x = k[0]
        temp_y = k[1]
        temp_address = destination_addresses[k]
        temp_json = {
                "geometry": {
                    "x": temp_x,
                    "y": temp_y,
                    "spatialReference": {
                        "wkid": "4326"
                        }
                    },
                "attributes": {
                    "Name": temp_address
                    }
                }
        features.append(temp_json)
    print("Length")
    print(len(features))

    facilities = { "features": features }




    print("FACILITIES")
    print(facilities)

    payload = {
            'f': 'json',
            'token': api_access_token,
            'returnDirections': 'false',
            'returnCFRoutes': 'false',
            'incidents': json.dumps(incidents),
            'facilities': json.dumps(facilities)
            }

    req = requests.Request('POST',base_url, data=payload)
    prepared = req.prepare()

    s = requests.Session()

    print(prepared.url)
    print(prepared.body)
    response = s.send(prepared)

    #response = requests.post(base_url, data=payload)

    if response.status_code != 200:
        logger.debug("Response Error: {}".format(str(response.status_code)))
        return None
    else:
        response_json = response.json()
        print(response_json)
        return None


   

def geocode_address_candidates(input_address):
    """
    Finds candidate addresses from ArcGIS Geocoding service
    based on input address string

    :param input_address: String of address to be geocoded
    :return: JSON object containing geocoded address candidates
    """

    logger.debug("Input Address: {}".format(input_address))

    base_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?"
    params_without_address = "f=json&outFields=Match_addr%2CAddr_type&singleLine=" 
    encoded_address = urllib.parse.quote(input_address)
    params_with_address = params_without_address + encoded_address

    request_url = base_url + params_with_address
    response = requests.get(request_url)

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
    logger.debug("Geocode Candidates \n" + str(candidates))

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

        logger.debug("Top Candidate: {}\n".format(address_string) \
                + "Candidate Score: {}".format(str(top_score)))

        coordinate_dict = {
                'address': address_string,
                'x': x_coordinate,
                'y': y_coordinate
                }
        return coordinate_dict


