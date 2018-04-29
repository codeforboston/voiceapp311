import mycity.test.intent_base_case as base_case


########################################
# TestCase class for unhandled intents #
########################################


class UnhandledIntentTestCase(base_case.IntentBaseCase):

    __test__ = True

    intent_to_test = "UnhandledIntent"
    returns_reprompt_text = True
