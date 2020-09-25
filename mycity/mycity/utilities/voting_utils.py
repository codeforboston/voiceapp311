import requests
import re
from mycity.intents.custom_errors import ParseError


def get_polling_location(ward_precinct):
    """
    Returns dictionary containing location name and address from
    the provided ward and precinct

    :param ward_precinct: dictionary object containing the ward and precinct
    :return: Dict containing location address string and
        location name string
    """

    ward = ward_precinct["ward"].lstrip()
    precinct = ward_precinct["precinct"].lstrip()
    url = "http://gis.cityofboston.gov/arcgis/rest/services/" \
        "CityServices/OpenData/MapServer/5/query"

    params = {
        "f": "json",
        "returnGeometry": "false",
        "where": "Ward = " + ward + "AND Precinct = " + precinct,
        "outFields": "Location2, Location3"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ParseError
    else:
        res_data = response.json()
        location_name = res_data['features'][0]['attributes']['Location2']
        location_address = res_data['features'][0]['attributes']['Location3']
        stripped_address = re.sub('[-]', '', location_address)
        stripped_name = re.sub('[-]', '', location_name)
        poll_location = {
            "Location Name": stripped_name,
            "Location Address": stripped_address
        }
        return poll_location


def get_ward_precinct_info(coordinates):
    """
    Returns dictionary containing location ward and precinct from the
    provided x, y coordinates

    :param coordinates: dictionary object containing the address
    string and floating point values for x and y that represent
    longitude and latitude
    :return: Dict containing ward string and precinct string
    """
    url = "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/" \
          "rest/services/Precincts_2017/FeatureServer/0/query"

    params = {
        "f": "json",
        "geometry": str(coordinates['x']) + "," + str(coordinates['y']),
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "returnGeometry": "false",
        "outFields": "WARD_PRECINCT"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise ParseError
    else:
        res_data = response.json()
        precinct_data = res_data['features'][0]['attributes']['WARD_PRECINCT']
        ward_precinct = {
            'ward': precinct_data[:2],
            'precinct': precinct_data[2:4]
        }
        return ward_precinct

