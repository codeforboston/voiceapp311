"""
Function(s) for dealing with unhandled intents
"""


def unhandled_intent(mcd):
    """
    Deals with unhandled intents by prompting the user again
    """
    print(
        '[module: unhandled_intent]',
        '[method: unhandled_intent]',
        'MyCityDataModel received:',
        str(mcd)
    )
    mcd.reprompt_text = "So, what can I help you with today?"
    mcd.output_speech = "I'm not sure what you're asking me. " \
                        "Please ask again."
    mcd.should_end_session = False

    return mcd
