"""Constants used across intents"""
import mycity.utilities.arcgis_utils as arcgis_utils

# The key used for the current address in session attributes
CURRENT_ADDRESS_KEY = "currentAddress"
ZIP_CODE_KEY = "Zipcode"

##################
# Common Constants
##################
BAD_API_RESPONSE = "Hmm something went wrong. Maybe try again?"
ADDRESS_NOT_FOUND = "I can't seem to find {}. Try another address"
ADDRESS_NOT_UNDERSTOOD = "I didn't understand that address, please try again " \
                         "with just the street number and name."

#################
# Fallback Intent
#################
REPROMPT_TEXT = "So, what can I help you with today?"
OUTPUT_SPEECH = "I'm not sure what you're asking me. " \
                "Please ask again about Boston services."

#################
# Feedback Intent
#################
BIG_THANKS = "Thanks for your feedback."
PROBLEM_SAVING_FEEDBACK = "There was a problem with your feedback. " \
                          "Please try again later."

###################
# Get Alerts Intent
###################
NO_ALERTS = "There are no alerts. City services are running on " \
            "normal schedules."
NO_INCLEMENT_WEATHER_ALERTS = "There are no weather related alerts"

############
# Latest 311
############
REQUEST_311_NUMBER_REPORTS_SLOT_NAME = "number_requests"
REQUEST_311_INTRO_SCRIPT = "Here are the {} latest three one one reports: "
REQUEST_311_REPORT_SCRIPT = \
    "There was a request at {} for the {} to address {}. "
REQUEST_311_CARD_TITLE = "311 Reports"

#################
# Location Speech
#################
GENERIC_GEOLOCATION_PERMISSION_SPEECH = """
    Boston Info would like to use your location. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions."""
GENERIC_DEVICE_PERMISSION_SPEECH = """
    Boston Info would like to use your device's address. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions."""
NOT_IN_BOSTON_SPEECH = 'This address is not in Boston. ' \
                       'Please use this skill with a Boston address. '\
                       'See you later!'

#####################
# Snow Parking Intent
#####################
OUTPUT_SPEECH_FORMAT = \
    ("The closest snow emergency parking lot, {Name}, is at {Address}. "
     "It is {" + arcgis_utils.DRIVING_DISTANCE_TEXT_KEY + "} away and "
     "should take you {" + arcgis_utils.DRIVING_TIME_TEXT_KEY + "} "
     "to drive there. The lot has {Spaces} spaces when empty. "
     "{Fee} {Comments} {Phone}")

# Formatted strings for the phone number and fee for the parking lot
PHONE_PREPARED_STRING = "Call {} for information."
FEE_PREPARED_STRING = " The fee is {}. "
NO_PHONE = ""
NO_FEE = " There is no fee. "

ERROR_SPEECH = "I need a valid address to find the closest parking"
ERROR_INVALID_ADDRESS = "I can't seem to find this address. " \
                        "Please make sure to provide both the street " \
                        "number and street name."
##############
# Trash Intent
##############
PICK_UP_DAY = "Trash and recycling is picked up on {}."
MULTIPLE_ADDRESS_ERROR = "I found multiple places with that address: {}. " \
                         "Which neighborhood is it in?"

