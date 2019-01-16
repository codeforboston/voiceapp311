"""
Controller for mycity voice app.

This class handles all voice requests.
"""

from mycity.mycity_response_data_model import MyCityResponseDataModel
from .intents.user_address_intent import set_address_in_session, \
    get_address_from_session, request_user_address_response, \
    set_zipcode_in_session, get_address_from_user_device
from mycity.intents.latest_311_intent import get_311_requests
from .intents.trash_intent import get_trash_day_info
from .intents.unhandled_intent import unhandled_intent
from .intents.get_alerts_intent import get_alerts_intent
from .intents.snow_parking_intent import get_snow_emergency_parking_intent
from .intents.feedback_intent import submit_feedback
from .intents.crime_activity_intent import get_crime_incidents_intent
from .intents import intent_constants
from .intents.food_truck_intent import get_nearby_food_trucks
import logging

logger = logging.getLogger(__name__)


def execute_request(mycity_request):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityRequestDataModel object corresponding to the request_type
    """
    # NOTE: The logger should be configured in the entry point from the
    #       platform (e.g., lambda_function for Alexa)
    logger.debug('Beginning request execution.')

    # TODO: This section should be generalized for all platforms if possible
    """
    Uncomment this if statement and populate with your skill's application ID 
    to prevent someone else from configuring a skill that sends requests to 
    this function.
    """
    # if (mcd.application_id !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if mycity_request.is_new_session:
        mycity_request = on_session_started(mycity_request)

    if mycity_request.request_type == "LaunchRequest":
        return on_launch(mycity_request)
    elif mycity_request.request_type == "IntentRequest":
        return on_intent(mycity_request)
    elif mycity_request.request_type == "SessionEndedRequest":
        return on_session_ended(mycity_request)


def on_session_started(mycity_request):
    """
    Called when the session starts. Creates a log entry with session info 
    and inserts device address into session attributes if available.

    :param mycity_request: MyCityRequestDataModel object
    :return: None
    """
    logger.debug('Request object: ' + mycity_request.get_logger_string())
    return get_address_from_user_device(mycity_request)


def on_launch(mycity_request):
    """
    Called when the user launches the skill without specifying what
    they want.

    :param mycity_request: MyCityRequestDataModel object with
        request_type LaunchRequest
    :return: MyCityResponseDataModel object that will initiate a welcome
        process on the user's device
    """
    logger.debug('')

    # Dispatch to your skill's launch
    return get_welcome_response(mycity_request)


def on_intent(mycity_request):
    """
    If the event type is "request" and the request type is "IntentRequest",
    this function is called to execute the logic associated with the
    provided intent and build a response. Checks for required
    session_attributes when applicable.
    
    :param mycity_request: MyCityRequestDataModel object with
        request_type IntentRequest
    :return: MyCityRequestDataModel object corresponding to the intent_name
    :raises: ValueError
    """

    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    if mycity_request.intent_name == "SetAddressIntent":
        set_address_in_session(mycity_request)
        return get_address_from_session(mycity_request)

    if "Address" in mycity_request.intent_variables \
            and "value" in mycity_request.intent_variables["Address"]:
        # Some of our intents have an associated address value.
        # Capture that into session data here
        set_address_in_session(mycity_request)

    if "Zipcode" in mycity_request.intent_variables \
        and "value" in mycity_request.intent_variables["Zipcode"]:
        set_zipcode_in_session(mycity_request)

    # session_attributes = session.get("attributes", {})
    if mycity_request.intent_name == "GetAddressIntent":
        return get_address_from_session(mycity_request)
    elif mycity_request.intent_name == "TrashDayIntent":
        return request_user_address_response(mycity_request) \
            if intent_constants.CURRENT_ADDRESS_KEY \
            not in mycity_request.session_attributes \
            else get_trash_day_info(mycity_request)
    elif mycity_request.intent_name == "SnowParkingIntent":
        return request_user_address_response(mycity_request) \
            if intent_constants.CURRENT_ADDRESS_KEY \
            not in mycity_request.session_attributes \
            else get_snow_emergency_parking_intent(mycity_request)
    elif mycity_request.intent_name == "CrimeIncidentsIntent":
        return request_user_address_response(mycity_request) \
            if intent_constants.CURRENT_ADDRESS_KEY \
            not in mycity_request.session_attributes \
            else get_crime_incidents_intent(mycity_request)
    elif mycity_request.intent_name == "GetAlertsIntent":
        return get_alerts_intent(mycity_request)
    elif mycity_request.intent_name == "AMAZON.HelpIntent":
        return get_help_response(mycity_request)
    elif mycity_request.intent_name == "AMAZON.StopIntent" or \
            mycity_request.intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request(mycity_request)
    elif mycity_request.intent_name == "FeedbackIntent":
        return submit_feedback(mycity_request)
    elif mycity_request.intent_name == "UnhandledIntent":
        return unhandled_intent(mycity_request)
    elif mycity_request.intent_name == "LatestThreeOneOne":
        return get_311_requests(mycity_request)
    elif mycity_request.intent_name == "FoodTruckIntent":
        return request_user_address_response(mycity_request) \
            if intent_constants.CURRENT_ADDRESS_KEY \
            not in mycity_request.session_attributes \
            else get_nearby_food_trucks(mycity_request)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(mycity_request):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true

    :param mycity_request: MyCityRequestDataModel object with
        request_type SessionEndedRequest
    :return: MyCityResponseDataModel object containing a clean instance
        of the response datamodel
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())
    
    return MyCityResponseDataModel()
    # add cleanup logic here


def get_help_response(mycity_request):
    """
    Provides an overview of the skill. This is triggered by AMAZON.HelpIntent.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object that will initiate
        a help process on the user's device
    """
    logger.debug('')
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Help"
    mycity_response.output_speech = (
        "You are using Boston Info, a skill that provides general information "
        "about Boston. You can currently ask about your trash and recycling "
        "pickup schedule, the location of the nearest snow emergency parking,"
        "and current alerts from Boston.gov. If you have feedback for the "
        "skill, say, 'I have a suggestion.'"
     )
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = False
    return mycity_response




def get_welcome_response(mycity_request):
    """
    Welcomes the user and sets initial session attributes. Is triggered on
    initial launch and on AMAZON.HelpIntent.

    If we wanted to initialize the session to have some attributes we could
    add those here.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object that will initiate
        a welcome process on the user's device
    """
    logger.debug('')
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Welcome"
    mycity_response.output_speech = \
        "Welcome to the Boston Info skill. How can I help you? "

    # If the user either does not reply to the welcome message or says
    # something that is not understood, they will be prompted again with
    # this text.
    mycity_response.reprompt_text = \
        "You can tell me your address by saying, " \
        "\"my address is\", and then your address."
    mycity_response.should_end_session = False
    return mycity_response


def handle_session_end_request(mycity_request):
    """
    Ends a user's session (with the Boston Info skill). Called when request
    intent is AMAZON.StopIntent or AMAZON.CancelIntent.
    
    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object that will end a user's session
    """
    logger.debug('Closing')
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Boston Info - Thanks"
    mycity_response.output_speech = \
        "Thank you for using the Boston Info skill. " \
        "See you next time!"
    mycity_response.should_end_session = True
    return mycity_response



