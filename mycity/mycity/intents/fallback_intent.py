"""
Function(s) for dealing with fallback intents
"""

from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.intents.intent_constants as intent_constants
import logging

CARD_TITLE = "Boston Info"
logger = logging.getLogger(__name__)


def fallback_intent(mycity_request):
    """
    Deals with unhandled intents by prompting the user again
    
    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug('MyCityRequestDataModel received:' + mycity_request.get_logger_string())
    
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = CARD_TITLE
    mycity_response.reprompt_text = intent_constants.REPROMPT_TEXT
    mycity_response.output_speech = intent_constants.OUTPUT_SPEECH
    mycity_response.should_end_session = False

    return mycity_response
