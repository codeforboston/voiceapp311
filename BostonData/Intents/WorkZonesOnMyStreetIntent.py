from lambda_function.lambda_function import *

def get_work_zones_on_my_street(intent, session):
    """
    Generates response object for work zones on my street inquiry
    """
    reprompt_text = None
    print("IN GET_WORKZONES_ONMYSTREET, SESSION: " + str(session))

    if "currentAddress" in session.get('attributes', {}):
        current_address = session['attributes']['currentAddress']
        speech_output = build_speech_work_zones(current_address)

    else:
        speech_output = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."

    session_attributes = session.get('attributes', {})
    should_end_session = False
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
