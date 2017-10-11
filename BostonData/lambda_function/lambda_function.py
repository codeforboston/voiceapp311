"""
Boston Data skill built using the Amazon color picker example:
http://amzn.to/1LzFrj6

This skill currently supports asking for the trash day associated with a
Boston address, which is provided in a slot.
"""

from __future__ import print_function
from streetaddress import StreetAddressFormatter, StreetAddressParser
import requests

def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
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
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


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
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SetAddressIntent":
        return set_address_in_session(intent, session)
    elif intent_name == "GetAddressIntent":
        return get_address_from_session(intent, session)
    elif intent_name == "TrashDayIntent":
        return get_trash_day_info(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request()
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

################################################################################
#--------------- Functions that control the skill's behavior ------------------#
################################################################################

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
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "For example, if your address is 1 Elm Street, apartment 2, say  " \
                    "my address is one elm street apartment 2."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def set_address_in_session(intent, session):
    """
    Sets the address in the session and prepares the speech to reply to the
    user.
    """
    # print("SETTING ADDRESS IN SESSION")
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Address' in intent['slots']:
        current_address = intent['slots']['Address']['value']
        session_attributes = create_current_address_attributes(current_address)
        speech_output = "I now know your address is " + \
                        current_address + \
                        ". Now you can ask questions related to your address" \
                        ". For example, when is trash day?"
        reprompt_text = "You can find out when trash is collected for your " \
                        "address by saying, when is trash day?"
    else:
        speech_output = "I'm not sure what your address is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_current_address_attributes(current_address):
    """
    Generates the currentAddress/address key/value pair.
    This key/value pair is used in set_address_in_session as the the session
    attributes.
    """
    return {"currentAddress": current_address}


def get_address_from_session(intent, session):
    """
    Looks for a current address in the session attributes and constructs a
    response based on whether one exists or not. If one exists, it is
    preserved in the session.
    """
    # print("GETTING ADDRESS FROM SESSION")
    session_attributes = {}
    reprompt_text = None

    if "currentAddress" in session.get('attributes', {}):
        current_address = session['attributes']['currentAddress']
        speech_output = "Your address is " + current_address + \
                        "."
        session_attributes = session.get('attributes', {})
        should_end_session = False
    else:
        speech_output = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_trash_day_info(intent, session):
    """
    Generates response object for a trash day inquiry.
    """
    reprompt_text = None
    print("IN GET_TRASH_DAY_INFO, SESSION: " + str(session))

    if "currentAddress" in session.get('attributes', {}):
        current_address = session['attributes']['currentAddress']

        # grab relevant information from session address
        addr_parser = StreetAddressParser()
        a = addr_parser.parse(current_address)
        # currently assumes that trash day is the same for all units at
        # the same street address
        address = str(a['house']) + " " + str(a['street_name'])

        # rest call to data.boston.gov for trash/recycle information
        url = 'https://data.boston.gov/api/action/datastore_search?' + \
              'resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q=' + \
              '{{"Address":"{}"}}'.format(address)
        resp = requests.get(url).json()
        print("RESPONSE FROM DATA.BOSTON.GOV: " + str(resp))

        # format script of response
        record = resp['result']['records'][0]
        speech_output = "Trash is picked up on the following days, " + \
                ", ".join(parseDays(record['Trash'])) + \
                ". Recycling is picked up on the following days, " + \
                " ,".join(parseDays(record['Recycling']))

        session_attributes = session.get('attributes', {})
        should_end_session = False
    else:
        session_attributes = session.get('attributes', {})
        speech_output = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def parseDays(days):
    """
    Converts the string of day initials in the JSON response to the trash
    day calendar API to a list of days.
    """
    result = []
    for i in range(len(days)):
        if days[i] == 'T':
            if i < len(days) - 1 and days[i+1] == 'H':
                result.append('Thursday')
            else:
                result.append('Tuesday')
        if days[i] == 'M':
            result.append('Monday')
        if days[i] == 'W':
            result.append('Wednesday')
        if days[i] == 'F':
            result.append('Friday')
    return result


def handle_session_end_request():
    card_title = "Boston Data - Thanks"
    speech_output = "Thank you for using the TrashApp skill.  See you next time!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
################################################################################
#--------------- Helpers that build all of the responses ----------------------#
################################################################################

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
