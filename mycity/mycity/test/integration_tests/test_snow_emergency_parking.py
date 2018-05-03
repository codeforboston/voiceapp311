import mycity.test.integration_tests.intent_base_case as base_case


##########################################
# TestCase class for snow_parking_intent #
##########################################

class SnowEmergencyTestCase(base_case.IntentBaseCase):

    __test__ = True

    intent_to_test = "SnowParkingIntent"
    returns_reprompt_text = False
