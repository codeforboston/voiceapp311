"""
Speech utterances for snow_parking_intent.py

"""
import mycity.utilities.arcgis_utils as arcgis_utils

OUTPUT_SPEECH_FORMAT = \
    ("The closest snow emergency parking lot, {Name}, is at "
     "{Address}. It is {" + arcgis_utils.DRIVING_DISTANCE_TEXT_KEY + "} away and should take "
     "you {" + arcgis_utils.DRIVING_TIME_TEXT_KEY + "} to drive there. The lot has "
     "{Spaces} spaces when empty. {Fee} {Comments} {Phone}")

# Formatted strings for the phone number and fee for the parking lot
PHONE_PREPARED_STRING = "Call {} for information."
FEE_PREPARED_STRING = " The fee is {}. "
NO_PHONE = ""
NO_FEE = " There is no fee. "

ERROR_SPEECH = "I need a valid address to find the closest parking"
