import unittest
import sys
from mycity.intents.unhandled_intent import unhandled_intent
from mycity.mycity_data_model import MyCityDataModel

class test_unhandled_intent(unittest.TestCase):

    def test_unhandled_intent(self):
        speech_expected = "I'm not sure what you're asking me. " \
                        "Please ask again."

        mcd = MyCityDataModel()
        mcd.request_type = "UnhandledIntent"
        mcd = unhandled_intent(mcd)
        self.assertEqual(mcd.output_speech, speech_expected)


if __name__ == '__main__':
    unittest.main()