"""
Boston Data Alexa skill.

This module is the entry point for processing voice data from an Alexa device.
"""

from mycity.mycity_data_model import MyCityDataModel
from mycity.mycity_controller import MyCityController


def lambda_handler(event, context):
    """
    Translate the Amazon request to a MC_Request_Model and call main.
    :param event: a dictionary containing event data
    :param context: a LambdaContext object containing runtime info
    """
    print(
        "[module: lambda_function]",
        "[function: lambda_handler]",
        "Amazon request received:\n",
        str(event)
    )

    model = platform_to_mcd(event)
    controller = MyCityController(model)
    return mcd_to_platform(controller.execute_request())


def platform_to_mcd(event):
    """
    Translates from Amazon platform request to MyCityDataModel

    :param event:
    :return:
    """
    print(
        "\n\n[module: lambda_function]",
        "[function: platform_to_mcd]",
        "Amazon request received:\n",
        str(event)
    )
    mcd = MyCityDataModel()
    mcd.request_type = event['request']['type']
    mcd.request_id = event['request']['requestId']
    mcd.is_new_session = event['session']['new']
    mcd.session_id = event['session']['sessionId']
    if 'attributes' in event['session']:
        mcd.session_attributes = event['session']['attributes']
    else:
        mcd.session_attributes = {}
    mcd.application_id = event['session']['application']['applicationId']
    if 'intent' in event['request']:
        mcd.intent_name = event['request']['intent']['name']
        if 'slots' in event['request']['intent']:
            mcd.intent_variables = event['request']['intent']['slots']
    else:
        mcd.intent_name = None
    mcd.output_speech = None
    mcd.reprompt_text = None
    mcd.should_end_session = False

    return mcd


def mcd_to_platform(mcd):
    """
    Translates from MyCityDataModel to Amazon platform response.

    The platform response contains:
    - a version number,
    - session information,
    - a response "speechlet" dictionary containing information on how Alexa
      responds to the user command.

    :param mcd:
    :return:
    """
    print(
        "\n\n[module: lambda_function]",
        "[function: mcd_to_platform]",
        "MyCityDataModel object received: " + str(mcd)
    )
    result = {
        'version': '1.0',
        'sessionAttributes': mcd.session_attributes,
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': mcd.output_speech
            },
            'card': {
                'type': 'Simple',
                'title': 'SessionSpeechlet - ' + str(mcd.intent_name),
                'content': 'SessionSpeechlet - ' + str(mcd.output_speech)
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': mcd.reprompt_text
                }
            },
            'shouldEndSession': mcd.should_end_session
        }
    }
    print('Result to platform:\n', result)
    return result
