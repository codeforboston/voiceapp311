"""
Farmers Market Intent
"""
import mycity.utilities.gis_utils as gis_utils
import logging
import datetime
from mycity.mycity_response_data_model import MyCityResponseDataModel
from .custom_errors import BadAPIResponse

logger = logging.getLogger(__name__)

BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/' \
           'services/Farmers_Markets_Fresh_Trucks_View/FeatureServer/0'
QUERY = {'where': '1=1', 'out_sr': '4326'}
DAY = datetime.datetime.today().strftime('%A')


def get_farmers_markets_today(mycity_request):
    """
    Get all available farmers markets today

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseObject
    """
    mycity_response = MyCityResponseDataModel()

    # List all available farmers markets today
    markets = gis_utils.get_features_from_feature_server(BASE_URL, QUERY)

    try:
        # Loop through the list of available farmers markets at a certain day
        markets_unique = []
        for m in markets:
            if m not in markets_unique and \
                    m['attributes']['Day_of_Week'] == DAY:
                markets_unique.append(m)

        response = 'Avaiable farmers markets today are:\n'
        for m in markets_unique:
            response += m['attributes']['Name'] + ' located at ' + \
                        m['attributes']['Address'] + ' from ' + \
                        m['attributes']['Hours'] + '. '
        mycity_response.output_speech = response

    except BadAPIResponse:
        mycity_response.output_speech = \
            "Hmm something went wrong. Maybe try again?"

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Farmers Markets"

    return mycity_response
