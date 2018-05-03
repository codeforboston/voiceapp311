import mycity.test.integration_tests.intent_base_case as base_case


########################################
# TestCase class for get_alerts_intent #
########################################

class GetAlertsTestCase(base_case.IntentBaseCase):

    __test__ = True

    intent_to_test = "GetAlertsIntent"
    returns_reprompt_text = False
