import mycity.test.integration_tests.intent_test_mixins as mix_ins
import mycity.test.integration_tests.intent_base_case as base_case


########################################
# TestCase class for unhandled intents #
########################################


class UnhandledIntentTestCase(mix_ins.RepromptTextTestMixIn,
                              mix_ins.CardTitleTestMixIn,
                              mix_ins.CorrectSpeechOutputTestMixIn,
                              base_case.IntentBaseCase):

    intent_to_test = "UnhandledIntent"
    expected_title = "Unhandled"
    returns_reprompt_text = True
