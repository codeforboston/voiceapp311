from mycity.intents import fallback_intent
from mycity.test.integration_tests.intent_base_case import IntentBaseCase
from mycity.test.integration_tests.intent_test_mixins import (
    CardTitleTestMixIn,
    CorrectSpeechOutputTestMixIn,
    RepromptTextTestMixIn,
)


########################################
# TestCase class for unhandled intents #
########################################


class FallbackIntentTestCase(RepromptTextTestMixIn,
                             CardTitleTestMixIn,
                             CorrectSpeechOutputTestMixIn,
                             IntentBaseCase):

    intent_to_test = "AMAZON.FallbackIntent"
    expected_title = fallback_intent.CARD_TITLE
    returns_reprompt_text = True
    expected_card_title = fallback_intent.CARD_TITLE
