"""
Functions for setting and getting the current user address
"""

from . import intent_constants


def set_address_in_session(mcd):
    """
    Adds an address to the provided session object

    :param mcd: MyCityRequestModel object
    """
    print(
        '[module: user_address_intent]',
        '[method: set_address_in_session]',
        'MyCityDataModel received:',
        str(mcd)
    )
    if 'Address' in mcd.intent_variables:
        mcd.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            mcd.intent_variables['Address']['value']


def get_address_from_session(mcd):
    """
    Looks for a current address in the session attributes and constructs a
    response based on whether one exists or not. If one exists, it is
    preserved in the session.

    :param mcd: MyCityDataModel
    :return:
    """
    print(
        '[module: user_address_intent]',
        '[method: get_address_from_session]',
        'MyCityDataModel received:',
        str(mcd)
    )

    # print("GETTING ADDRESS FROM SESSION")
    mcd.reprompt_text = None
    mcd.should_end_session = False

    if intent_constants.CURRENT_ADDRESS_KEY in mcd.session_attributes:
        current_address = mcd.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY]
        mcd.output_speech = "Your address is " + current_address + "."
    else:
        mcd.output_speech = "I'm not sure what your address is. " \
                            "You can tell me your address by saying, " \
                            "\"my address is\" followed by your address."

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. They will be returned to the top level of the skill and must
    # provide input that corresponds to an intent to continue.

    return mcd


def request_user_address_response(mcd):
    """
    Creates a response to request the user's address

    :param mcd: MyCityRequestModel object
    :return: MyCityRequestModel object
    """
    print(
        '[module: user_address_intent]',
        '[method: set_address_in_session]',
        'MyCityDataModel received:',
        str(mcd)
    )

    mcd.session_attributes[intent_constants.ADDRESS_PROMPTED_FROM_INTENT] = \
        mcd.intent_name
    mcd.output_speech = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "\"my address is\" followed by your address."
    mcd.should_end_session = False
    mcd.reprompt_text = None
    return mcd
