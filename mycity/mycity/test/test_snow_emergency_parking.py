import mycity.intents.snow_parking_intent
import mycity.test.integration_test_parent as itp


##########################################
# TestCase class for snow_parking_intent #
##########################################


class SnowEmergencyTestCase(itp.IntegrationTestCaseParent):

    def setUp(self):
        super(SnowEmergencyTestCase, self).setUp()
        self.request.intent_name = "SnowParkingIntent"

    def tearDown(self):
        super(SnowEmergencyTestCase, self).tearDown()

    def test_for_smoke(self):
        response = self.controller.on_intent(self.request)
        self.assertNotIn("Uh oh", response.output_speech)
        self.assertNotIn("Error", response.output_speech)

    def test_correct_intent_card_title(self):
        response = self.controller.on_intent(self.request)
        self.assertEqual("SnowParkingIntent", response.card_title)

    def test_returning_no_reprompt_text(self):
        response = self.controller.on_intent(self.request)
        self.assertIsNone(response.reprompt_text)
