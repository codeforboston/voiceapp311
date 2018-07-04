"""
Functions for setting and getting the current user address
"""

from . import intent_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
import requests
import logging

logger = logging.getLogger(__name__)


def set_address_in_session(mycity_request):
    """
    Adds an address to the provided session object

    :param mycity_request: MyCityRequestDataModel object
    :return: None
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    if 'Address' in mycity_request.intent_variables:
        mycity_request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            mycity_request.intent_variables['Address']['value']

        if intent_constants.ZIP_CODE_KEY in mycity_request.session_attributes:
            # We clear out any zip code saved if the user has
            # changed the address
            del(mycity_request.session_attributes
                [intent_constants.ZIP_CODE_KEY])


def set_zipcode_in_session(mycity_request):
    """
    Adds a zip code to the provided request object.

    :param mycity_request: MyCityRequestsDataModel object
    :return: none
    """
    if 'Zipcode' in mycity_request.intent_variables:
        mycity_request.session_attributes[intent_constants.ZIP_CODE_KEY] = \
            mycity_request.intent_variables['Zipcode']['value'].zfill(5)


def get_address_from_user_device(mycity_request):
    """
    checks Amazon api for device address permissions. 
    If given, the address, if present, will be stored 
    in the session attributes

    :param mycity_request: MyCityRequestDataModel
    :param mycity_response: MyCityResponseDataModel
    :return : MyCityRequestModel object
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    base_url = "https://api.amazonalexa.com/v1/devices/{}" \
        "/settings/address".format(mycity_request.device_id)
    head_info = {'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(mycity_request.api_access_token)}
    response_object = requests.get(base_url, headers=head_info)

    if response_object.status_code == 200:
        res = response_object.json()
        if res['addressLine1'] is not None:
            current_address = res['addressLine1']
            mycity_request.session_attributes[
                intent_constants.CURRENT_ADDRESS_KEY] = current_address
    return mycity_request


def get_address_from_session(mycity_request):
    """
    Looks for a current address in the session attributes and constructs a
    response based on whether one exists or not. If one exists, it is
    preserved in the session.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()
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
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())

    mycity_response = MyCityResponseDataModel()

    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.should_end_session = False
    mycity_response.output_speech = "What's your address?"
    mycity_response.card_title = "Address"
    mycity_response.dialog_directive = "Delegate"
    return mycity_response


def clear_address_from_mycity_object(mycity_object):
    """
    Removes any address info from a mycity object session attribute

    :param mycity_object: Either a MyCityResponseDataModel or
        MyCityRequestDataModel
    :return: MyCity object with attributes removed
    """
    if intent_constants.ZIP_CODE_KEY in mycity_object.session_attributes:
        del(mycity_object.session_attributes[intent_constants.ZIP_CODE_KEY])

    if intent_constants.CURRENT_ADDRESS_KEY in mycity_object.session_attributes:
        del(mycity_object.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY])

    return mycity_object