"""
The feedback intent allows the user to provide feedback about the skill,
including bug reports and suggestions for new intents.
"""

import json
import os

import requests

from mycity.intents.speech_constants import feedback_intent as speech_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel

SLACK_WEBHOOKS_URL = os.environ['SLACK_WEBHOOKS_URL']
CARD_TITLE = "Feedback"


def submit_feedback(mycity_request):
    """
    Logs user feedback to the mycity-feedback slack channel.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    print(
        '[module: feedback_intent]',
        '[method: submit_feedback]',
        'MyCityRequestDataModel received:',
        mycity_request.get_logger_string()
    )
    # get the intent_variables object from the request
    intent_variables = mycity_request.intent_variables

    # Build the response.
    #   - if we are missing the feedback type or feedback text, we'll delegate
    #     to the dialog model to request the missing information
    #   - if we have everything we need, we'll pose the message to slack and
    #     confirm to the user
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.should_end_session = False
    if (
            'value' not in intent_variables['FeedbackType'] or
            'value' not in intent_variables['Feedback']
    ):
        mycity_response.intent_variables = intent_variables
        mycity_response.dialog_directive = "Delegate"
        return mycity_response
    else:
        feedback_type = intent_variables['FeedbackType']['value']
        feedback_text = intent_variables['Feedback']['value']

        try:
            status = send_to_slack(
                build_slack_message(feedback_type, feedback_text)
            )
            if status == 200:
                mycity_response.output_speech = speech_constants.BIG_THANKS
            else:
                mycity_response.output_speech = speech_constants.PROBLEM_SAVING_FEEDBACK
        except Exception:
            mycity_response.output_speech = speech_constants.PROBLEM_SAVING_FEEDBACK

        mycity_response.reprompt_text = None
        mycity_response.session_attributes = mycity_request.session_attributes
        mycity_response.card_title = CARD_TITLE
    return mycity_response


def send_to_slack(message):
    """
    Posts feedback in the mycity-feedback Slack channel via HTTP request.

    :param message:
    :return:
    """
    print(
        '[module: feedback_intent]',
        '[method: send_to_slack]',
        'message received:',
        message
    )
    data = json.dumps({'text': message})
    headers = {'Content-Type': 'application/json'}
    request = requests.post(SLACK_WEBHOOKS_URL, data, headers)
    return request.status_code


def build_slack_message(feedback_type, feedback_text):
    """
    Configures the message we will post to slack.

    :param feedback_type:
    :param feedback_text:
    :return:
    """
    print(
        '[module: feedback_intent]',
        '[method: build_slack_message]',
        'feedback type and text received:',
        feedback_type + ', ' + feedback_text
    )
    emoji = ':bug:' if feedback_type == 'bug' else ':bulb:'
    return emoji + '\n>' + feedback_text
