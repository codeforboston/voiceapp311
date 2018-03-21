"""
Function(s) for dealing with unhandled intents
"""

from alexa_utilities import build_response, build_speechlet_response


def unhandled_intent(intent, session):
    """
    Deals with unhandled intents by prompting the user again
    """
    reprompt_text = "So, what can I help you with today?"
    speech_output = "I'm not sure what you're asking me. " \
                    "Please ask again."
    session_attributes = session.get('attributes', {})
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session))