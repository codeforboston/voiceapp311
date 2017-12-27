"""
Functions for setting and getting the current user address
"""

from alexa_utilities import build_response, build_speechlet_response
import alexa_constants


def set_address_in_session(intent, session):
    """
    Adds an address from the set address intent to the provided session object

    :param intent: SetAddress intent object
    :param session: Current session object
    """

    if 'Address' in intent['slots']:
        current_address = intent['slots']['Address']['value']
        if "attributes" not in session:
            session["attributes"] = {}
        session["attributes"].update(
            create_current_address_attributes(current_address))


def create_set_address_intent_response(intent, session):
    card_title = intent['name']
    session_attributes = session["attributes"]
    should_end_session = False

    if 'Address' in intent['slots']:
        current_address = intent['slots']['Address']['value']
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
    return {alexa_constants.CURRENT_ADDRESS_KEY: current_address}


def get_address_from_session(intent, session):
    """
    Looks for a current address in the session attributes and constructs a
    response based on whether one exists or not. If one exists, it is
    preserved in the session.
    """
    # print("GETTING ADDRESS FROM SESSION")
    session_attributes = {}
    reprompt_text = None

    if alexa_constants.CURRENT_ADDRESS_KEY in session.get('attributes', {}):
        current_address = session['attributes'][alexa_constants.CURRENT_ADDRESS_KEY]
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


def request_user_address_response(intent, session):
    """
    Creates a response to request the user's address
    :param intent: Intent that reqested the user address
    :param session: Current session object
    :return: Alexa response object
    """
    session_attributes = session.get('attributes', {})
    session_attributes[alexa_constants.ADDRESS_PROMPTED_FROM_INTENT] \
        = intent["name"]
    speech_output = "I'm not sure what your address is. " \
                    "You can tell me your address by saying, " \
                    "my address is 123 Main St., apartment 3."
    should_end_session = False
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
