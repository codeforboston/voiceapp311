import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case
import mycity.intents.fallback_intent as fallback_intent


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
