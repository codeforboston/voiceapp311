from lambda_function.lambda_function import *


def get_work_zones_on_any_street(intent, session):
    '''
    Generates response object for work zones on any street inquiry
    '''
    reprompt_text = None
    print("IN GET_WORKZONES_ONANYSTREET, SESSION: " + str(session))

    if 'TargetAddress' in intent['slots']:
        target_address = intent['slots']['TargetAddress']['value']
        speech_output = build_speech_work_zones(target_address)

    else:
        speech_output = "I'm not sure what the street name is. " \
                        "You can ask for information on active work zones by saying, " \
                        "is there any street work going on Washington Street"

    session_attributes = session.get('attributes', {})
    should_end_session = False
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
