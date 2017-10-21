"""
Boston Data skill built using the Amazon color picker example:
http://amzn.to/1LzFrj6

This skill currently supports asking for the trash day associated with a
Boston address, which is provided in a slot.
"""

from __future__ import print_function
from streetaddress import StreetAddressFormatter, StreetAddressParser
from Intents.SetAddressIntent import *
from Intents.GetAddressIntent import *
from Intents.TrashDayIntent import *
from Intents.WorkZonesOnMyStreetIntent import *
from Intents.WorkZonesOnAnyStreetIntent import *
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


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


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
    elif intent_name == "WorkZonesOnMyStreetIntent":
        return get_work_zones_on_my_street(intent, session)
    elif intent_name == "WorkZonesOnAnyStreetIntent":
        return get_work_zones_on_any_street(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


################################################################################
#----------------------- Helper Functions for Intents -------------------------#
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


def create_current_address_attributes(current_address):
    """
    Generates the currentAddress/address key/value pair.
    This key/value pair is used in set_address_in_session as the the session
    attributes.
    """
    return {"currentAddress": current_address}


def build_speech_work_zones(current_address):

    # grab relevant information from user given address
    addr_parser = StreetAddressParser().parse(current_address)
    address = str(addr_parser['street_name'])

    # rest call to data.boston.gov for active work zone information
    url = 'https://data.boston.gov/api/3/action/datastore_search?' + \
          'resource_id=36fcf981-e414-4891-93ea-f5905cec46fc&q=' + \
          '{{"Street":"{}"}}'.format(address)
    resp = requests.get(url).json()
    print("RESPONSE FROM DATA.BOSTON.GOV: " + str(resp))

    # format script of response
    if resp['result']['records']:
        record = resp['result']['records'][0]
        zone_str = ''
        start = ''
        if int(record['_full_count']) > 1:
            zone_str = 'zones'
            start = 'There are'
        else:
            zone_str = 'zone'
            start = 'There is'

        speech_output = start + " " + "".join(record['_full_count']) + " " + "active work" + " " + \
                        "".join(zone_str) + " " + "on that street."

    else:
        speech_output = "There are no active work zones on that street."
    return speech_output


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
