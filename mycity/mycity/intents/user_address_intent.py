"""
Functions for setting and getting the current user address
"""

from . import intent_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel

def set_address_in_session(mycity_request):
    """
    Adds an address to the provided session object

    :param mycity_request: MyCityRequestDataModel object
    :return: none
    """
    print(
        '[module: user_address_intent]',
        '[method: set_address_in_session]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    if 'Address' in mycity_request.intent_variables:
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            mycity_request.intent_variables['Address']['value']


def get_address_from_session(mycity_request):
    """
    Looks for a current address in the session attributes and constructs a
    response based on whether one exists or not. If one exists, it is
    preserved in the session.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    print(
        '[module: user_address_intent]',
        '[method: get_address_from_session]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    # print("GETTING ADDRESS FROM SESSION")
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Address"
    mycity_response.reprompt_text = None
    mycity_response.should_end_session = False

    if intent_constants.CURRENT_ADDRESS_KEY in mycity_request.session_attributes:
        current_address = mycity_request.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY]
        mycity_response.output_speech = "Your address is " + current_address + "."
    else:
        mycity_response.output_speech = "I'm not sure what your address is. " \
                                        "You can tell me your address by saying, " \
                                        "\"my address is\" followed by your address."

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. They will be returned to the top level of the skill and must
    # provide input that corresponds to an intent to continue.

    return mycity_response


def request_user_address_response(mycity_request):
    """
    Creates a response to request the user's address

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    print(
        '[module: user_address_intent]',
        '[method: set_address_in_session]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()

    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.should_end_session = False
    mycity_response.output_speech = "What's your address?"
    mycity_response.card_title = "Address"
    mycity_response.dialog_directive = "Delegate"
    return mycity_response
