"""
Controller for mycity voice app.

This class handles all voice requests.
"""

from __future__ import print_function
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel
from .intents.user_address_intent import set_address_in_session, \
    get_address_from_session, request_user_address_response
from .intents.trash_intent import get_trash_day_info
from .intents.unhandled_intent import unhandled_intent
from .intents.get_alerts_intent import get_alerts_intent
from .intents.snow_parking_intent import get_snow_emergency_parking_intent
from .intents import intent_constants


LOG_CLASS = '\n\n[class: MyCityController]'


def execute_request(mycity_request):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.

    :param mycity_request: event request object formatted for mycity_controller
    :return: method call based on type of request
    """
    print(
        LOG_CLASS,
        '[method: main]',
        'MyCityRequestDataModel received:\n',
        str(mycity_request)
    )

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
        on_session_started(mycity_request)

    if mycity_request.request_type == "LaunchRequest":
        return on_launch(mycity_request)
    elif mycity_request.request_type == "IntentRequest":
        return on_intent(mycity_request)
    elif mycity_request.request_type == "SessionEndedRequest":
        return on_session_ended(mycity_request)


def on_session_started(mycity_request):
    """
    Called when the session starts. Creates a log entry with session info.

    :param mycity_request: event request object formatted for mycity_controller
    :return: none
    """
    print(
        LOG_CLASS,
        '[method: on_session_started]',
        '[requestId: ' + str(mycity_request.request_id) + ']',
        '[sessionId: ' + str(mycity_request.session_id) + ']',
        (
            '[request object: ' + str(mycity_request) + ']' if
            isinstance(mycity_request, MyCityRequestDataModel) else
            '[request object: ' +
            'ERROR - request should be a MyCityRequestDataModel.]'
        )
    )

def on_launch(mycity_request):
    """
    Called when the user launches the skill without specifying what
    they want.

    :param mycity_request: event request object formatted for mycity_controller
        with request_type LaunchRequest
    :return: method that initiates user welcome
    """
    print(
        LOG_CLASS,
        '[method: on_launch]',
        '[requestId: ' + str(mycity_request.request_id) + ']',
        '[sessionId: ' + str(mycity_request.session_id) + ']'
    )

    # Dispatch to your skill's launch
    return get_welcome_response(mycity_request)


def on_intent(mycity_request):
    """
    If the event type is "request" and the request type is "IntentRequest",
    this function is called to execute the logic associated with the
    provided intent and build a response. Checks for required
    session_attributes when applicable.
    
    :param mycity_request: event request object formatted for mycity_controller
        with request_type IntentRequest
    :return: method based on request intent
    """

    print(
        LOG_CLASS,
        '[method: on_intent]',
        '[intent: ' + mycity_request.intent_name + ']',
        'MyCityRequestDataModel received:',
        mycity_request
    )

    # Check if the user is setting the address. This is special cased
    # since they may have been prompted for this info from another intent
    if mycity_request.intent_name == "SetAddressIntent":
        set_address_in_session(mycity_request)

        if intent_constants.ADDRESS_PROMPTED_FROM_INTENT \
                in mycity_request.session_attributes:
            # User was prompted for address from another intent.
            # Set our current intent to be that original intent now that
            # we have set the address.
            mycity_request.intent_name = mycity_request.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT]
            print("Address set after calling another intent. Redirecting "
                  "intent to {}".format(mycity_request.intent_name))
            # Delete the session key indicating this intent was called
            # from another intent.
            del mycity_request.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT]
        else:
            return get_address_from_session(mycity_request)

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
    elif mycity_request.intent_name == "GetAlertsIntent":
        return get_alerts_intent(mycity_request)
    elif mycity_request.intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(mycity_request)
    elif mycity_request.intent_name == "AMAZON.StopIntent" or \
            mycity_request.intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request(mycity_request)
    elif mycity_request.intent_name == "UnhandledIntent":
        return unhandled_intent(mycity_request)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(mycity_request):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true

    :param mycity_request: event request object formatted for mycity_controller
        with request_type SessionEndedRequest
    :return MyCityResponseDataModel(): response object formatted for Alexa
        service platform containing a clean instance of the response datamodel
    """
    print(
        LOG_CLASS,
        '[method: on_session_ended]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    return MyCityResponseDataModel()
    # add cleanup logic here


def get_welcome_response(mycity_request):
    """
    Welcomes the user and sets initial session attributes. Is triggered on
    initial launch and on AMAZON.HelpIntent.

    If we wanted to initialize the session to have some attributes we could
    add those here.

    :param mycity_request: event request object formatted for mycity_controller
    :return mycity_response: response object formatted for Alexa service
        platform that initiates a welcome process on the user's device
    """
    print(
        LOG_CLASS,
        '[method: get_welcome_response]'
    )
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Welcome"
    mycity_response.output_speech = \
        "Welcome to the Boston Public Services skill. How can I help you? "

    # If the user either does not reply to the welcome message or says
    # something that is not understood, they will be prompted again with
    # this text.
    mycity_response.reprompt_text = \
        "For example, you can tell me your address by saying, " \
        "\"my address is\" followed by your address."
    mycity_response.should_end_session = False
    return mycity_response


def handle_session_end_request(mycity_request):
    """
    Ends a user's session (with the Boston Data skill). Called when request
    intent is AMAZON.StopIntent or AMAZON.CancelIntent.
    
    :param mycity_request: event request object formatted for mycity_controller
    :return mycity_response: response object formatted for Alexa service
        platform that ends a user's session
    """
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Boston Public Services - Thanks"
    mycity_response.output_speech = \
        "Thank you for using the Boston Public Services skill. " \
        "See you next time!"
    mycity_response.should_end_session = True
    return mycity_response



