"""
Function(s) for dealing with unhandled intents
"""

from mycity.mycity_response_data_model import MyCityResponseDataModel

def unhandled_intent(mycity_request):
    """
    Deals with unhandled intents by prompting the user again
    
    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    print(
        '[module: unhandled_intent]',
        '[method: unhandled_intent]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "UnhandledIntent"
    mycity_response.reprompt_text = "So, what can I help you with today?"
    mycity_response.output_speech = "I'm not sure what you're asking me. " \
                        "Please ask again."
    mycity_response.should_end_session = False

    return mycity_response
