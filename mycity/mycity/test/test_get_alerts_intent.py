from mycity.intents.get_alerts_intent import get_alerts_intent, prune_normal_responses, alerts_to_speech_output
from mycity.mycity_data_model import MyCityDataModel
import unittest

class test_get_alerts_intent(unittest.TestCase):

    def setUp(self):
        self.serviceAlert = {'Trash and recycling':'Pickup in on a normal schedule.',
                                'Tow lot':'The tow lot is open from 7 a.m. - 11 p.m. ' \
                                'Automated kiosks are available 24 hours a day, '\
                                'seven days a week for vehicle releases.'}
        self.emptyAlerts = {}

    # I'll come back to this once I figure out mocking http rest calls
    #
    # def test_get_alerts_intent(self):
    #     mcd = MyCityDataModel()
    #     mcd = get_alerts_intent(mcd)
    #     print (mcd)

    def test_prune_normal_responses(self):
        service_alerts = prune_normal_responses(self.serviceAlert)
        self.assertEqual(bool(service_alerts), False)

    def test_alerts_to_speech_output(self):
        expected_result = "There are no alerts. City services are operating on their normal schedule."
        returned_result = alerts_to_speech_output(self.emptyAlerts)
        self.assertEqual(returned_result, expected_result)


if __name__ == '__main__':
    unittest.main()