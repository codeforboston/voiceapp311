from mycity.intents import fallback_intent
from mycity.test.integration_tests import (
    intent_base_case as base_case,
    intent_test_mixins as mix_ins,
)

########################################
# TestCase class for unhandled intents #
########################################


class FallbackIntentTestCase(mix_ins.RepromptTextTestMixIn,
                              mix_ins.CardTitleTestMixIn,
                              mix_ins.CorrectSpeechOutputTestMixIn,
                              base_case.IntentBaseCase):

    intent_to_test = "AMAZON.FallbackIntent"
    expected_title = fallback_intent.CARD_TITLE
    returns_reprompt_text = True
    expected_card_title = fallback_intent.CARD_TITLE
