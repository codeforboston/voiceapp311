"""
Boston Data Alexa skill.

This skill currently supports asking for the trash day associated with a
Boston address.

Based the Amazon color picker example:
http://amzn.to/1LzFrj6
"""

from __future__ import print_function
from user_address_intent import set_address_in_session, \
    get_address_from_session
from trash_intent import get_trash_day_info
from unhandled_intent import unhandled_intent
from alexa_utilities import build_speechlet_response, build_response
from snow_parking_intent import get_snow_emergency_parking_intent


def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID 
    to prevent someone else from configuring a skill that sends requests to 
    this function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """
    Called when the session starts.
    """
    print(" ".join(["on_session_started requestId=",
                   session_started_request['requestId'],
                   ", sessionId=" + session['sessionId']]))


def on_launch(launch_request, session):
    """
    Called when the user launches the skill without specifying what they want.
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """
    If the event type is "request" and the request type is "IntentRequest",
    this function is called to execute the logic associated with the provided
    intent and build a response.
    """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("on_intent requestId={}, sessionId={}, intent_name={}"
          .format(intent, session['sessionId'], intent_name))

    # Dispatch to your skill's intent handlers
    if intent_name == "SetAddressIntent":
        return set_address_in_session(intent)
    elif intent_name == "GetAddressIntent":
        return get_address_from_session(intent, session)
    elif intent_name == "TrashDayIntent":
        return get_trash_day_info(intent, session)
    elif intent_name == "SnowParkingIntent":
        return get_snow_emergency_parking_intent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent" or \
                    intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request()
    elif intent_name == "UnhandledIntent":
        return unhandled_intent(intent, session) 
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def get_welcome_response():
    """
    If we wanted to initialize the session to have some attributes we could
    add those here.
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Boston Data skill. " \
                    "To set your address, say " \
                    "my address is, followed by your address."
    # If the user either does not reply to the welcome message or says
    # something that is not understood, they will be prompted again with
    # this text.
    reprompt_text = "For example, if your address is 1 Elm Street, " \
                    "apartment 2, say my address is one elm street " \
                    "apartment 2."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Boston Data - Thanks"
    speech_output = "Thank you for using the TrashApp skill. " \
                    "See you next time!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title,
                                                       speech_output,
                                                       None,
                                                       should_end_session))
