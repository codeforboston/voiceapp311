import mycity.intents.test.integration_test_parent




class IntegrationTestFactory:
    
    class __IntegrationTestFactory:
        def __init__(self):
            """
            Don't really need to do anything here
            """
        
        def createTestCase(self, intent_name):
            """
            Return an a TestCase object inheriting from
            IntegrationTestCaseParent.  This TestCase will assume that an
            address has already been set and tests that the speech_output is not
            an error_message (eg. starts with "Error" or "Uh oh" and the
            title_card for that intent matches the intent_name

            """

            
