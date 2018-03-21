import sys
sys.path.append('/Users/Joshhw/Documents/code/codeforboston/voiceapp311/BostonData/lambda_function') 
import unittest
import json
import os.path
from lambda_function import get_welcome_response, lambda_handler

class test_all_intents(unittest.TestCase):

    def test_getWelcomeSpeech(self):
        resp = get_welcome_response()
        output = resp['response']['outputSpeech']['text']
        self.assertEqual(output, 'Welcome to the Boston Public Services skill. How can I help you?')

    def test_trash_intent_without_address(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(os.path.join(my_path, "intent_folder/intent.json"))
        test_json = json.load(open(path))
        resp = lambda_handler(test_json,test_json['context'])
        self.assertEqual(resp['response']['outputSpeech']['text'], "I'm not sure what your address is. "\
            "You can tell me your address by saying, my address is 123 Main St., apartment 3.")

    def test_address_intent_with_get_address(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(os.path.join(my_path, "intent_folder/address.json"))
        test_json = json.load(open(path))
        resp = lambda_handler(test_json,test_json['context'])
        self.assertEqual(resp['response']['outputSpeech']['text'], "Your address is 866 Huntington ave.")

    def test_set_address_intent_with_set_address_on(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(os.path.join(my_path, "intent_folder/trashdata.json"))
        test_json = json.load(open(path))
        resp = lambda_handler(test_json,test_json['context'])
        self.assertEqual(resp['response']['outputSpeech']['text'], "Trash is picked up on the following "\
            "days, Tuesday, Friday. Recycling is picked up on the following days, Tuesday")

    def test_snow_intent_with_snow_emergency(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(os.path.join(my_path, "intent_folder/snow.json"))
        test_json = json.load(open(path))
        resp = lambda_handler(test_json,test_json['context'])
        self.assertEqual(resp['response']['outputSpeech']['text'], "The closest snow emergency "\
            "parking location is at 490-498 Centre St Boston, MA. It is 1.1 mi away and should take "\
            "you 6 mins to drive there")


if __name__ == '__main__':
    unittest.main()