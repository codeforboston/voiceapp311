import sys
sys.path.append('/Users/Joshhw/Documents/code/codeforboston/voiceapp311/BostonData/lambda_function') 
import unittest
from lambda_function import get_welcome_response
class test_string_methods(unittest.TestCase):

    def test_getWelcomeSpeech(self):
        resp = get_welcome_response()
        output = resp['response']['outputSpeech']['text']
        self.assertEqual(output, 'Welcome to the Boston Public Services skill. How can I help you?')

if __name__ == '__main__':
    unittest.main()