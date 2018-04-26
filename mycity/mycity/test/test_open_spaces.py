import mycity.intents.get_open_spaces_intent
import mycity.test.integration_test_case_prototype as itp


#########################################
# TestCase class for open_spaces_intent #
#########################################


class GetOpenSpacesTestCase(itp.IntegrationTestCasePrototype):

    def setUp(self):
        super().setUp()
        self.intent_to_test = "GetOpenSpacesIntent"
        self.request.intent_name = self.intent_to_test

    def tearDown(self):
        super().tearDown()

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

