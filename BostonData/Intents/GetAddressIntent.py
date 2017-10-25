from ..lambda_function.lambda_function import build_response, build_speechlet_response


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
