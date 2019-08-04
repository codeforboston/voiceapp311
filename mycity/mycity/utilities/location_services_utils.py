"""Methods for determining location base permissions and extracting the location data"""

import mycity.mycity_response_data_model as mycity_response_data_model

GENERIC_GEOLOCATION_PRERMISSON_SPEECH = """
    Boston Info would like to use your location. 
    To turn on location sharing, please go to your Alexa app and follow the instructions."""

def request_geolocation_permission_response():
    """
    Builds a response object for requesting geolocation permissions. The
    returned object's speech can be modified if you want to add more information

    :return MyCityResponseDataModel: MyCityResponseDataModel with required fields
        to request geolocation access
    """
    response = mycity_response_data_model.MyCityResponseDataModel()
    response.output_speech = GENERIC_GEOLOCATION_PRERMISSON_SPEECH
    response.card_type = "AskForPermissionsConsent"
    response.card_permissions = ["alexa::devices:all:geolocation:read"]
    response.should_end_session = True
    return response


def convert_mycity_coordinates_to_arcgis(mycity_request):
    """
    Gets coordinates from a MyCityRequestDataModel and converts them to dictionary
    required by GIS utilities
    """
    gis_coordinates = {
        'x': 0,
        'y': 0
    }
    
    if mycity_request.geolocation_coordinates:
        gis_coordinates['y'] = mycity_request.geolocation_coordinates["latitudeInDegrees"]
        gis_coordinates['x'] = mycity_request.geolocation_coordinates["longitudeInDegrees"]

    return gis_coordinates