import mycity.test.integration_tests.intent_base_case as base_case


###################################
# TestCase class for trash_intent #
###################################

class TrashDayTestCase(base_case.IntentBaseCase):

    __test__ = True

    intent_to_test = "TrashDayIntent"
    returns_reprompt_text = False
