from ..lambda_function.lambda_function import build_speechlet_response, build_response, create_current_address_attributes


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
