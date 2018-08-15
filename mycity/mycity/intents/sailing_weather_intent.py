"""
Alexa intent used to find the sailing weather conditions
on the Charles River
"""

import requests
import re
import datetime

from mycity.mycity_response_data_model import MyCityResponseDataModel


COMMUNITY_SAILING = "https://api2.community-boating.org/api/flag"
GREEN_CONDITION = "The sailing conditions are currently green at Community Boating."
YELLOW_CONDITION = "The sailing conditions are currently yellow at Community Boating."
RED_CONDITION = "The sailing conditions are currently red at Community Boating."
CLOSED_CONDITION = "Community Boating is currently closed."
ERROR_CONDITION = "Sailing weather information for Community Boating is currently unavailable. Please try again later."
CLOSED_FOR_SEASON_CONDITION = "Community Boating is closed for the Season. It will re-open in April"


def get_sailing_weather_intent(mycity_request):
    """
    Retrieves the sailing conditions from Community Boating's API
    and provides it to the user in an easily digestible format.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    print(
        '[method: get_sailing_weather_intent]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    mycity_response = MyCityResponseDataModel()

    r = requests.get("https://api2.community-boating.org/api/flag")

    mycity_response.output_speech = get_sailing_conditions(r.text)
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Community Boating Sailing Conditions"
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = True
    return mycity_response

def get_sailing_conditions(api_response):
    """
    Checks for validity and parses the string returned from the API

    :param api_response: string indicating current sailing conditions
    :return: string with message detailing current sailing conditions
    """
    
    try:
        trimmed_flag_msg = re.search('.*var\sFLAG_COLOR\s=\s"([RYCG])".*', api_response).group(1)
    except:
        # Throw an error if the formatting doesn't match
        output = ERROR_CONDITION
        return output
    
    # server_flag_msg = api_response  # Ex:     var FLAG_COLOR = "Y"
    if trimmed_flag_msg == 'G':
        output = GREEN_CONDITION
    elif trimmed_flag_msg == 'Y':
        output = YELLOW_CONDITION
    elif trimmed_flag_msg == 'R':
        output = RED_CONDITION
    elif trimmed_flag_msg == 'C':
        now = datetime.datetime.now()
        if ((now.month > 10) or (now.month < 4)):
            output = CLOSED_FOR_SEASON_CONDITION
        else:
            output = CLOSED_CONDITION
    else:
        output = ERROR_CONDITION
    return output
