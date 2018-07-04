"""Alexa intent used to find snow emergency parking"""


import mycity.intents.intent_constants as intent_constants
import mycity.utilities.google_maps_utils as g_maps_utils
from mycity.utilities.finder.FinderCSV import FinderCSV
from mycity.mycity_response_data_model import MyCityResponseDataModel
import logging

logger = logging.getLogger('[method: get_snow_emergency_parking_intent]')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Constants 
PARKING_INFO_URL = ("http://bostonopendata-boston.opendata.arcgis.com/datasets/"
                    "53ebc23fcc654111b642f70e61c63852_0.csv")
DRIVING_DIST = g_maps_utils.DRIVING_DISTANCE_TEXT_KEY
DRIVING_TIME = g_maps_utils.DRIVING_TIME_TEXT_KEY
OUTPUT_SPEECH_FORMAT = \
    ("The closest snow emergency parking location, {Name}, is at "
     "{Address}. It is {" + DRIVING_DIST + "} away and should take "
     "you {" + DRIVING_TIME + "} to drive there. The parking lot has "
     "{Spaces} spaces when empty. {Fee} {Comments} {Phone}")
ADDRESS_KEY = "Address"


def format_record_fields(record):
   record["Phone"] = "Call {} for information.".format(record["Phone"]) \
       if record["Phone"].strip() != "" else ""
   record["Fee"] = " There is a fee of {}. ".format(record["Fee"]) \
       if record["Fee"] != "No Charge" else " There is no fee. "
   

def get_snow_emergency_parking_intent(mycity_request):
    """
    Populate MyCityResponseDataModel with snow emergency parking response information.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug(
        'MyCityRequestDataModel received:' +
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        finder = FinderCSV(mycity_request, PARKING_INFO_URL, ADDRESS_KEY, 
                           OUTPUT_SPEECH_FORMAT, format_record_fields)
        print("Finding snow emergency parking for {}".format(finder.origin_address))
        finder.start()
        mycity_response.output_speech = finder.get_output_speech()

    else:
        print("Error: Called snow_parking_intent with no address")

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    mycity_response.reprompt_text = None
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = mycity_request.intent_name
    
    return mycity_response


