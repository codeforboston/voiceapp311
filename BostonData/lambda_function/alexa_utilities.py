"""
Common utilities for building Alexa skills
"""


def build_response(session_attributes, speechlet_response):
    """
    Formats a response to an Alexa request.
    
    :param session_attributes: Dictionary containing information that
        persists the entire Alexa session.
    :param speechlet_response: Dictionary containing speechlet response.
        Construct using build_speechlet_response()
    :return: Dictionary containing a full Alexa response
    """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Creates a "speechlet" dictionary. This speechlet information on how Alexa
    responds to the user command.

    :param title: Title of card to render in the Alexa app
    :param output: Speech to respond with. Also shows up in the Alex app
        card content.
    :param reprompt_text: Output speech if a re-prompt is necessary.
    :param should_end_session: boolean indicating if we should end the current
        session.
    :return: Dictionary of entire speechlet.
    """
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
