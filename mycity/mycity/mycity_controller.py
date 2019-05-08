"""
Controller for mycity voice app.

This class handles all voice requests.

"""

import logging

from mycity.intents import intent_constants
from mycity.intents.crime_activity_intent import get_crime_incidents_intent
from mycity.intents.fallback_intent import fallback_intent
from mycity.intents.farmers_market_intent import get_farmers_markets_today
from mycity.intents.feedback_intent import submit_feedback
from mycity.intents.food_truck_intent import get_nearby_food_trucks
from mycity.intents.get_alerts_intent import get_alerts_intent, get_inclement_weather_alert
from mycity.intents.latest_311_intent import get_311_requests
from mycity.intents.snow_parking_intent import get_snow_emergency_parking_intent
from mycity.intents.trash_intent import get_trash_day_info
from mycity.intents.user_address_intent import (
    set_address_in_session,
    get_address_from_session,
    request_user_address_response,
    set_zipcode_in_session,
    get_address_from_user_device,
)
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel

logger = logging.getLogger(__name__)

LAUNCH_SPEECH = "Welcome to the Boston Info skill. You can ask for help at any time, and I'll " \
                "let you know what information I can provide. " \
                "How can I help you?"

LAUNCH_REPROMPT_SPEECH = "You can ask me about Boston city services, " \
                         "such as \"are there any city alerts\"?"

HELP_SPEECH = "You are using Boston Info, a skill that provides information " \
              "about Boston services and alerts. You can ask about your trash " \
              "pickup schedule, city alerts, the locations of food trucks " \
              "and farmers markets, info about snow emergencies, the latest " \
              "three one one reports, and the latest crime reports! " \
              "If you have feedback for the skill, say, 'I have a suggestion.'"


def execute_request(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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


def on_session_started(mycity_request: MyCityRequestDataModel) -> MyCityRequestDataModel:
    """
    Called when the session starts. Creates a log entry with session info
    and inserts device address into session attributes if available.

    :param mycity_request: MyCityRequestDataModel object
    :return: None
    """
    logger.debug('Request object: ' + mycity_request.get_logger_string())
    return get_address_from_user_device(mycity_request)


def on_launch(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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


def on_intent(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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
    elif mycity_request.intent_name == "FoodTruckIntent":
        return request_user_address_response(mycity_request) \
            if intent_constants.CURRENT_ADDRESS_KEY \
               not in mycity_request.session_attributes \
            else get_nearby_food_trucks(mycity_request)
    elif mycity_request.intent_name == "GetAlertsIntent":
        return get_alerts_intent(mycity_request)
    elif mycity_request.intent_name == "AMAZON.HelpIntent":
        return get_help_response(mycity_request)
    elif mycity_request.intent_name == "AMAZON.StopIntent" or \
            mycity_request.intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request(mycity_request)
    elif mycity_request.intent_name == "FeedbackIntent":
        return submit_feedback(mycity_request)
    elif mycity_request.intent_name == "AMAZON.FallbackIntent":
        return fallback_intent(mycity_request)
    elif mycity_request.intent_name == "LatestThreeOneOne":
        return get_311_requests(mycity_request)
    elif mycity_request.intent_name == "InclementWeatherIntent":
        return get_inclement_weather_alert(mycity_request)
    elif mycity_request.intent_name == "FarmersMarketIntent":
        return get_farmers_markets_today(mycity_request)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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


def get_help_response(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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
    mycity_response.output_speech = HELP_SPEECH
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = False
    return mycity_response


def get_welcome_response(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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
    mycity_response.output_speech = LAUNCH_SPEECH

    # If the user either does not reply to the welcome message or says
    # something that is not understood, they will be prompted again with
    # this text.
    mycity_response.reprompt_text = LAUNCH_REPROMPT_SPEECH
    mycity_response.should_end_session = False
    return mycity_response


def handle_session_end_request(mycity_request: MyCityRequestDataModel) -> MyCityResponseDataModel:
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
