"""
Boston Info Alexa skill.

This module is the entry point for processing voice data from an Alexa device.
"""

import logging
import traceback

from mycity.intents.feedback_intent import build_slack_traceback, send_to_slack
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_controller import execute_request

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Translate the Amazon request to a MC_Request_Model and call main.

    :param event: JSON object containing the raw request information received
        from the Alexa service platform
    :param context: a LambdaContext object containing runtime info
    :return: JSON response object to be sent to the Alexa service platform
    """
    # Handle logger configuration here at the first use of the logger
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])
    logging.basicConfig(
        format='%(levelname)-8s %(name)-20s %(funcName)-12s: %(message)s',
        level=logging.DEBUG
    )
    logger.debug('Amazon request received: ' + str(event))

    try:
        model = platform_to_mycity_request(event)
        return mycity_response_to_platform(execute_request(model))
    except Exception as error:
        trace = traceback.format_exc()
        send_to_slack(build_slack_traceback(error, trace))
        raise


def _get_location_services_info(event: object,
                                mycity_request: object) -> object:
    """
    Adds Alexa location services to MyCityRequestDataModel

    :param event: event JSON object provided by Alexa
    :param mycity_request: MyCityRequestDataModel to add location service info to
    :return MyCityRequestDataModel: The new MyCityRequestDataModel containing
        location service info
    """
    # Determine geolocation services support
    system_context = event['context']['System']
    device_context = system_context.get('device', {})
    supported_interfaces = device_context.get("supportedInterfaces", {})
    mycity_request.device_has_geolocation = "Geolocation" in \
                                            supported_interfaces

    # Determine permissions
    if mycity_request.device_has_geolocation:
        mycity_request.geolocation_permission = "Geolocation" in \
                                                event["context"]

    # Get coordinates
    if mycity_request.geolocation_permission:
        mycity_request.geolocation_coordinates = \
            event["context"]["Geolocation"].get("coordinate", {})

    return mycity_request


def platform_to_mycity_request(event):
    """
    Translates from Amazon platform request to MyCityRequestDataModel

    :param event: JSON object containing the raw request information received
        from the Alexa service platform
    :return: MyCityRequestDataModel object (formatted to be understood and
        acted on by mycity_controller)
    """
    logger.debug('Amazon request received: ' + str(event))
    mycity_request = MyCityRequestDataModel()

    # Get base request information
    mycity_request.request_type = event['request']['type']
    mycity_request.request_id = event['request']['requestId']

    # Get session information
    mycity_request.is_new_session = event['session']['new']
    mycity_request.session_id = event['session']['sessionId']
    mycity_request.application_id = \
        event['session']['application']['applicationId']

    # Get device information
    system_context = event['context']['System']
    device_context = system_context.get('device', {})
    mycity_request.device_id = device_context.get('deviceId', "unknown")
    mycity_request.api_access_token = \
        system_context.get('apiAccessToken', "none")

    # Get location services info
    mycity_request = _get_location_services_info(event, mycity_request)

    if 'attributes' in event['session']:
        mycity_request.session_attributes = event['session']['attributes']
    else:
        mycity_request.session_attributes = {}
    
    if 'intent' in event['request']:
        mycity_request.intent_name = event['request']['intent']['name']
        if 'slots' in event['request']['intent']:
            mycity_request.intent_variables = \
                event['request']['intent']['slots']
    else:
        mycity_request.intent_name = None
    mycity_request.output_speech = None
    mycity_request.reprompt_text = None
    mycity_request.should_end_session = False

    return mycity_request


def mycity_response_to_platform(mycity_response):
    """
    Translates from MyCityResponseDataModel to Amazon platform response.

    The platform response contains:
    - a version number,
    - session information,
    - a response "speechlet" dictionary containing information on how Alexa
      responds to the user command.

    :param mycity_response: MyCityResponseDataModel object generated by
        mycity_controller executing a request
    :return: JSON response object that will be sent to the Alexa
        service platform
    """
    logger.debug('MyCityResponseDataModel object received: ' +
                 mycity_response.get_logger_string())

    if mycity_response.dialog_directive:
        if mycity_response.dialog_directive['type'] == "Dialog.Delegate":
            response = {
                'directives': [
                    mycity_response.dialog_directive
                ],
                'card': {
                    'type': 'Simple',
                    'title': str(mycity_response.card_title),
                    'content': str(mycity_response.output_speech)
                    }
            }
        else:
            response = {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': mycity_response.output_speech
                },
                'card': {
                    'type': str(mycity_response.card_type),
                    'title': str(mycity_response.card_title),
                    'content': str(mycity_response.output_speech)
                },
                'reprompt': {
                 'outputSpeech': {
                        'type': 'PlainText',
                        'text': mycity_response.reprompt_text
                 }
                },
                'shouldEndSession': mycity_response.should_end_session,
                'directives': [
                    mycity_response.dialog_directive
                    ]
            }
    else:
        response = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': mycity_response.output_speech
            },
            'card': {
                'type': str(mycity_response.card_type),
                'title': str(mycity_response.card_title),
                'content': str(mycity_response.output_speech)
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': mycity_response.reprompt_text
                }
            },
            'shouldEndSession': mycity_response.should_end_session
        }

    if mycity_response.card_permissions:
        response['card']['permissions'] = mycity_response.card_permissions

    if mycity_response.dialog_directive == "Dialog.ElicitSlot":
        # Add the slot we want to elicit on top of the normal output.
        logger.debug('Setting elicit slot options.')
        response["directives"] = [
            {
                "type": mycity_response.dialog_directive,
                "slotToElicit": mycity_response.slot_to_elicit
            }]

    result = {
        'version': '1.0',
        'sessionAttributes': mycity_response.session_attributes,
        'response': response
    }
    logger.debug('Result to platform:' + str(result))
    return result
